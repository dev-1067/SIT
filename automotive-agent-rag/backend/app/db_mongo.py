"""Manual metadata + file storage.

Primary backend: MongoDB (metadata in a `manuals` collection, raw PDF bytes
in GridFS) so uploaded manuals persist centrally and are listed back to the
user the next time they open the app, exactly like a real document store.

If no MongoDB server is reachable (e.g. MONGODB_URI not configured yet),
the app falls back to an equivalent JSON+disk store so the product still
works end-to-end instead of hard failing. The API reports which backend is
active via GET /api/health so this is never silent.
"""
import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from bson import ObjectId
from pymongo.errors import PyMongoError

from . import config, mongo_client

logger = logging.getLogger("automotive_rag.db")


class ManualsRepository:
    backend_name = "base"

    def list_manuals(self) -> List[dict]:
        raise NotImplementedError

    def find_manual(self, brand: str, model: str, year: str) -> Optional[dict]:
        raise NotImplementedError

    def get_manual(self, manual_id: str) -> Optional[dict]:
        raise NotImplementedError

    def insert_manual(self, meta: dict, file_bytes: bytes, filename: str) -> dict:
        raise NotImplementedError

    def update_manual_fields(self, manual_id: str, fields: dict) -> None:
        raise NotImplementedError

    def get_file(self, manual_id: str) -> Optional[bytes]:
        raise NotImplementedError

    def delete_all(self) -> None:
        raise NotImplementedError


def _serialize(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    out.pop("gridfs_file_id", None)
    if isinstance(out.get("uploaded_at"), datetime):
        out["uploaded_at"] = out["uploaded_at"].isoformat()
    return out


class MongoManualsRepository(ManualsRepository):
    backend_name = "mongodb"

    def __init__(self, uri: str, db_name: str):
        import gridfs

        self.client = mongo_client.connect(uri)
        self.db = self.client[db_name]
        self.manuals = self.db["manuals"]
        self.fs = gridfs.GridFS(self.db, collection="manual_files")

    def list_manuals(self) -> List[dict]:
        return [_serialize(d) for d in self.manuals.find().sort("uploaded_at", 1)]

    def find_manual(self, brand: str, model: str, year: str) -> Optional[dict]:
        doc = self.manuals.find_one(
            {
                "brand": {"$regex": f"^{brand}$", "$options": "i"},
                "model": {"$regex": f"^{model}$", "$options": "i"},
                "year": str(year),
            }
        )
        return _serialize(doc) if doc else None

    def get_manual(self, manual_id: str) -> Optional[dict]:
        doc = self.manuals.find_one({"_id": ObjectId(manual_id)})
        return _serialize(doc) if doc else None

    def insert_manual(self, meta: dict, file_bytes: bytes, filename: str) -> dict:
        gridfs_id = self.fs.put(file_bytes, filename=filename)
        doc = {
            **meta,
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc),
            "gridfs_file_id": gridfs_id,
        }
        result = self.manuals.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    def update_manual_fields(self, manual_id: str, fields: dict) -> None:
        self.manuals.update_one({"_id": ObjectId(manual_id)}, {"$set": fields})

    def get_file(self, manual_id: str) -> Optional[bytes]:
        doc = self.manuals.find_one({"_id": ObjectId(manual_id)})
        if not doc or "gridfs_file_id" not in doc:
            return None
        return self.fs.get(doc["gridfs_file_id"]).read()

    def delete_all(self) -> None:
        for doc in self.manuals.find():
            if "gridfs_file_id" in doc:
                try:
                    self.fs.delete(doc["gridfs_file_id"])
                except Exception:  # noqa: BLE001
                    pass
        self.manuals.delete_many({})


class LocalManualsRepository(ManualsRepository):
    """Disk-backed fallback used only when MongoDB is unreachable."""

    backend_name = "local_fallback"

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.files_dir = base_dir / "files"
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.meta_path = base_dir / "manuals.json"
        if not self.meta_path.exists():
            self.meta_path.write_text("[]")

    def _read(self) -> List[dict]:
        try:
            return json.loads(self.meta_path.read_text())
        except Exception:  # noqa: BLE001
            return []

    def _write(self, records: List[dict]) -> None:
        self.meta_path.write_text(json.dumps(records, indent=2))

    def list_manuals(self) -> List[dict]:
        return self._read()

    def find_manual(self, brand: str, model: str, year: str) -> Optional[dict]:
        for rec in self._read():
            if (
                rec["brand"].strip().lower() == brand.strip().lower()
                and rec["model"].strip().lower() == model.strip().lower()
                and str(rec["year"]).strip() == str(year).strip()
            ):
                return rec
        return None

    def get_manual(self, manual_id: str) -> Optional[dict]:
        for rec in self._read():
            if rec["id"] == manual_id:
                return rec
        return None

    def insert_manual(self, meta: dict, file_bytes: bytes, filename: str) -> dict:
        records = self._read()
        manual_id = uuid.uuid4().hex
        (self.files_dir / f"{manual_id}.pdf").write_bytes(file_bytes)
        record = {
            **meta,
            "id": manual_id,
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
        records.append(record)
        self._write(records)
        return record

    def update_manual_fields(self, manual_id: str, fields: dict) -> None:
        records = self._read()
        for rec in records:
            if rec["id"] == manual_id:
                rec.update(fields)
                break
        self._write(records)

    def get_file(self, manual_id: str) -> Optional[bytes]:
        path = self.files_dir / f"{manual_id}.pdf"
        if not path.exists():
            return None
        return path.read_bytes()

    def delete_all(self) -> None:
        self._write([])
        if self.files_dir.exists():
            shutil.rmtree(self.files_dir)
        self.files_dir.mkdir(parents=True, exist_ok=True)


_repository: Optional[ManualsRepository] = None


def get_repository() -> ManualsRepository:
    global _repository
    if _repository is not None:
        return _repository
    try:
        _repository = MongoManualsRepository(config.MONGODB_URI, config.MONGODB_DB_NAME)
        logger.info("Connected to MongoDB at %s", config.MONGODB_URI)
    except PyMongoError as exc:
        logger.warning(
            "MongoDB unreachable (%s). Falling back to local disk-based manual storage. "
            "Set MONGODB_URI in .env to enable persistent MongoDB storage.",
            exc,
        )
        _repository = LocalManualsRepository(config.LOCAL_FALLBACK_DIR)
    return _repository


def reset_repository_cache() -> None:
    global _repository
    _repository = None
