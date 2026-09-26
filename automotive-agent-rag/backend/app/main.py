import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import agent, auth, config, key_check, pdf_utils, vector_store
from .db_mongo import get_repository
from .schemas import (
    AuthResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LoginRequest,
    ManualOut,
    PreloadedManualStatus,
    ProviderModelInfo,
    RegisterRequest,
    UploadResponse,
    UserOut,
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
    try:
        count = len(repo.list_manuals())
        backend_name = repo.backend_name
    except Exception:
        from .db_mongo import LocalManualsRepository, reset_repository_cache
        reset_repository_cache()
        repo = LocalManualsRepository(config.LOCAL_FALLBACK_DIR)
        count = len(repo.list_manuals())
        backend_name = repo.backend_name

    return HealthResponse(
        status="ok",
        storage_backend=backend_name,
        manuals_indexed=count,
    )


@app.post("/api/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    try:
        user, token = auth.register(req.email, req.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthResponse(token=token, user=UserOut(**user))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest):
    try:
        user, token = auth.login(req.email, req.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return AuthResponse(token=token, user=UserOut(**user))


@app.post("/api/auth/logout")
def logout(token: str = Depends(auth.get_current_token)):
    auth.logout(token)
    return {"status": "ok"}


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: dict = Depends(auth.get_current_user)):
    return UserOut(**current_user)


@app.get("/api/providers")
def list_providers(current_user: dict = Depends(auth.get_current_user)) -> dict[str, ProviderModelInfo]:
    return agent.get_provider_status()


@app.get("/api/providers/verify")
def verify_providers(current_user: dict = Depends(auth.get_current_user)):
    """Makes one lightweight real call per configured provider to confirm the
    key in backend/.env actually authenticates. Lets you self-diagnose
    'invalid API key' errors without needing anyone else to look at logs."""
    return key_check.verify_all_providers()


@app.get("/api/manuals", response_model=list[ManualOut])
def list_manuals(current_user: dict = Depends(auth.get_current_user)):
    repo = get_repository()
    return [_to_manual_out(r) for r in repo.list_manuals()]


@app.get("/api/manuals/preloaded", response_model=list[PreloadedManualStatus])
def list_preloaded_manuals(current_user: dict = Depends(auth.get_current_user)):
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
def preload_manual(key: str, current_user: dict = Depends(auth.get_current_user)):
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
    current_user: dict = Depends(auth.get_current_user),
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
def reset_all(current_user: dict = Depends(auth.get_current_user)):
    repo = get_repository()
    repo.delete_all()
    vector_store.reset_index()
    return {"status": "reset"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, current_user: dict = Depends(auth.get_current_user)):
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
        if "credit_balance_exhausted" in err_msg or ("insufficient_quota" in err_msg and req.provider == "openai"):
            raise HTTPException(
                status_code=402,
                detail="OpenAI account credit balance is exhausted ($0 balance). Please add credits at https://platform.openai.com/billing or switch provider to Groq (100% free) in the sidebar."
            ) from exc
        if any(s in err_msg for s in ("RESOURCE_EXHAUSTED", "free_tier_requests")):
            raise HTTPException(
                status_code=429,
                detail="Google Gemini free-tier daily quota limit reached. Please select 'gemini-flash-lite-latest' or switch provider to Groq (100% free) in the sidebar."
            ) from exc
        if any(s in err_msg for s in ("insufficient_quota", "429", "rate_limit")):
            raise HTTPException(
                status_code=429, detail="Rate limit reached for this provider/model. Please wait a moment or switch to Groq in the sidebar."
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
        if any(s in err_msg for s in ("Connection error", "ConnectError", "getaddrinfo failed", "ConnectTimeout")):
            raise HTTPException(
                status_code=503,
                detail=f"Network connection to {req.provider.capitalize()} servers timed out or dropped. Please check your internet connection or switch provider to Groq."
            ) from exc
        raise HTTPException(status_code=500, detail=f"An error occurred: {err_msg}") from exc
