import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import agent, config, key_check, pdf_utils, vector_store
from .db_mongo import get_repository
from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ManualOut,
    PreloadedManualStatus,
    ProviderModelInfo,
    UploadResponse,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Automotive RAG Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_manual_out(record: dict) -> ManualOut:
    return ManualOut(
        id=record["id"],
        brand=record["brand"],
        model=record["model"],
        year=str(record["year"]),
        filename=record["filename"],
        source=record.get("source", "uploaded"),
        num_pages=record.get("num_pages", 0),
        num_chunks=record.get("num_chunks", 0),
        uploaded_at=record["uploaded_at"],
        preload_key=record.get("preload_key"),
    )


def _index_manual(file_bytes: bytes, filename: str, brand: str, model: str, year: str, source: str, preload_key: str | None = None) -> ManualOut:
    pages = pdf_utils.extract_pages(file_bytes)
    if not any(p.strip() for p in pages):
        raise HTTPException(status_code=400, detail="Could not extract any readable text from the provided PDF.")

    repo = get_repository()
    meta = {
        "brand": brand.strip(),
        "model": model.strip(),
        "year": str(year).strip(),
        "source": source,
        "num_pages": len(pages),
        "preload_key": preload_key,
    }
    record = repo.insert_manual(meta, file_bytes, filename)

    chunks = pdf_utils.build_chunks(pages, brand.strip(), model.strip(), str(year).strip(), record["id"], filename)
    vector_store.add_documents(chunks)

    record["num_chunks"] = len(chunks)
    repo.update_manual_fields(record["id"], {"num_chunks": len(chunks)})
    return _to_manual_out(record)


@app.get("/api/health", response_model=HealthResponse)
def health():
    repo = get_repository()
    return HealthResponse(
        status="ok",
        storage_backend=repo.backend_name,
        manuals_indexed=len(repo.list_manuals()),
    )


@app.get("/api/providers")
def list_providers() -> dict[str, ProviderModelInfo]:
    return agent.get_provider_status()


@app.get("/api/providers/verify")
def verify_providers():
    """Makes one lightweight real call per configured provider to confirm the
    key in backend/.env actually authenticates. Lets you self-diagnose
    'invalid API key' errors without needing anyone else to look at logs."""
    return key_check.verify_all_providers()


@app.get("/api/manuals", response_model=list[ManualOut])
def list_manuals():
    repo = get_repository()
    return [_to_manual_out(r) for r in repo.list_manuals()]


@app.get("/api/manuals/preloaded", response_model=list[PreloadedManualStatus])
def list_preloaded_manuals():
    repo = get_repository()
    result = []
    for key, info in config.PRELOADED_MANUALS.items():
        match = repo.find_manual(info["brand"], info["model"], info["year"])
        result.append(
            PreloadedManualStatus(
                key=key,
                label=info["label"],
                brand=info["brand"],
                model=info["model"],
                year=info["year"],
                loaded=match is not None,
            )
        )
    return result


@app.post("/api/manuals/preload/{key}", response_model=UploadResponse)
def preload_manual(key: str):
    info = config.PRELOADED_MANUALS.get(key)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Unknown preloaded manual '{key}'.")

    repo = get_repository()
    existing = repo.find_manual(info["brand"], info["model"], info["year"])
    if existing:
        return UploadResponse(manual=_to_manual_out(existing), num_chunks=existing.get("num_chunks", 0))

    pdf_path = config.MANUALS_DIR / info["filename"]
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail=f"Bundled manual file missing on server: {info['filename']}")

    file_bytes = pdf_path.read_bytes()
    manual = _index_manual(
        file_bytes, info["filename"], info["brand"], info["model"], info["year"], source="preloaded", preload_key=key
    )
    return UploadResponse(manual=manual, num_chunks=manual.num_chunks)


@app.post("/api/manuals/upload", response_model=UploadResponse)
async def upload_manual(
    file: UploadFile = File(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: str = Form(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    manual = _index_manual(file_bytes, file.filename, brand, model, year, source="uploaded")
    return UploadResponse(manual=manual, num_chunks=manual.num_chunks)


@app.get("/api/manuals/{manual_id}/file")
def get_manual_file(manual_id: str):
    repo = get_repository()
    record = repo.get_manual(manual_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Manual not found.")
    file_bytes = repo.get_file(manual_id)
    if file_bytes is None:
        raise HTTPException(status_code=404, detail="Manual file not found in storage.")
    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{record["filename"]}"'},
    )


@app.delete("/api/manuals")
def reset_all():
    repo = get_repository()
    repo.delete_all()
    vector_store.reset_index()
    return {"status": "reset"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        answer, evidence = agent.run_chat(
            message=req.message,
            provider=req.provider,
            model_name=req.model,
            brand=req.brand,
            vehicle_model=req.vehicle_model,
            year=req.year,
        )
        return ChatResponse(answer=answer, evidence=evidence)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        err_msg = str(exc)
        if any(s in err_msg for s in ("API_KEY_INVALID", "incorrect_api_key", "Invalid API Key", "invalid_api_key")):
            raise HTTPException(status_code=401, detail="Invalid API key configured in the backend .env file.") from exc
        if any(s in err_msg for s in ("insufficient_quota", "RESOURCE_EXHAUSTED", "429", "rate_limit")):
            raise HTTPException(
                status_code=429, detail="Rate limit reached. Please wait a moment or select another AI provider."
            ) from exc
        if any(
            s in err_msg
            for s in ("model_not_found", "model_decommissioned", "does not exist", "has been decommissioned", "404")
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The selected model is not available on this provider's account ({err_msg[:200]}). "
                    "Please pick a different model from the dropdown."
                ),
            ) from exc
        raise HTTPException(status_code=500, detail=f"An error occurred: {err_msg}") from exc
