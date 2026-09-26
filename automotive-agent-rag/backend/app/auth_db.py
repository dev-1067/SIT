"""User + session storage for authentication.

Mirrors the primary/fallback pattern used in db_mongo.py: MongoDB is the
real backend (a `users` collection and a `sessions` collection), with an
equivalent on-disk JSON store as a fallback so login still works if Mongo
isn't reachable.
"""
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from . import config

logger = logging.getLogger("automotive_rag.auth_db")

SESSION_TTL = timedelta(days=7)


class AuthRepository:
    backend_name = "base"

    def create_user(self, email: str, password_hash: str) -> dict:
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> Optional[dict]:
        raise NotImplementedError

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        raise NotImplementedError

    def create_session(self, user_id: str) -> str:
        raise NotImplementedError

    def get_session_user_id(self, token: str) -> Optional[str]:
        raise NotImplementedError

    def delete_session(self, token: str) -> None:
        raise NotImplementedError


def _serialize_user(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]) if "_id" in doc else doc["id"],
        "email": doc["email"],
        "created_at": doc["created_at"].isoformat() if isinstance(doc["created_at"], datetime) else doc["created_at"],
    }


class MongoAuthRepository(AuthRepository):
    backend_name = "mongodb"

    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        self.client.admin.command("ping")
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.sessions = self.db["sessions"]
        self.users.create_index("email", unique=True)
        self.sessions.create_index("token", unique=True)
        self.sessions.create_index("expires_at", expireAfterSeconds=0)

    def create_user(self, email: str, password_hash: str) -> dict:
        from bson import ObjectId

        doc = {"_id": ObjectId(), "email": email, "password_hash": password_hash, "created_at": datetime.now(timezone.utc)}
        try:
            self.users.insert_one(doc)
        except DuplicateKeyError as exc:
            raise ValueError("An account with this email already exists.") from exc
        return _serialize_user(doc)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        doc = self.users.find_one({"email": email})
        return doc

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        from bson import ObjectId

        try:
            doc = self.users.find_one({"_id": ObjectId(user_id)})
        except Exception:  # noqa: BLE001
            return None
        return _serialize_user(doc) if doc else None

    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self.sessions.insert_one(
            {
                "token": token,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + SESSION_TTL,
            }
        )
        return token

    def get_session_user_id(self, token: str) -> Optional[str]:
        doc = self.sessions.find_one({"token": token})
        return doc["user_id"] if doc else None

    def delete_session(self, token: str) -> None:
        self.sessions.delete_one({"token": token})


class LocalAuthRepository(AuthRepository):
    """Disk-backed fallback used only when MongoDB is unreachable."""

    backend_name = "local_fallback"

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.users_path = base_dir / "users.json"
        self.sessions_path = base_dir / "sessions.json"
        if not self.users_path.exists():
            self.users_path.write_text("[]")
        if not self.sessions_path.exists():
            self.sessions_path.write_text("[]")

    def _read(self, path: Path) -> list:
        try:
            return json.loads(path.read_text())
        except Exception:  # noqa: BLE001
            return []

    def _write(self, path: Path, records: list) -> None:
        path.write_text(json.dumps(records, indent=2))

    def create_user(self, email: str, password_hash: str) -> dict:
        users = self._read(self.users_path)
        if any(u["email"] == email for u in users):
            raise ValueError("An account with this email already exists.")
        user = {
            "id": uuid.uuid4().hex,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        users.append(user)
        self._write(self.users_path, users)
        return _serialize_user(user)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        for u in self._read(self.users_path):
            if u["email"] == email:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        for u in self._read(self.users_path):
            if u["id"] == user_id:
                return _serialize_user(u)
        return None

    def create_session(self, user_id: str) -> str:
        sessions = self._read(self.sessions_path)
        token = secrets.token_urlsafe(32)
        sessions.append(
            {
                "token": token,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + SESSION_TTL).isoformat(),
            }
        )
        self._write(self.sessions_path, sessions)
        return token

    def get_session_user_id(self, token: str) -> Optional[str]:
        now = datetime.now(timezone.utc).isoformat()
        for s in self._read(self.sessions_path):
            if s["token"] == token and s["expires_at"] > now:
                return s["user_id"]
        return None

    def delete_session(self, token: str) -> None:
        sessions = self._read(self.sessions_path)
        sessions = [s for s in sessions if s["token"] != token]
        self._write(self.sessions_path, sessions)


_repository: Optional[AuthRepository] = None


def get_auth_repository() -> AuthRepository:
    global _repository
    if _repository is not None:
        return _repository
    try:
        _repository = MongoAuthRepository(config.MONGODB_URI, config.MONGODB_DB_NAME)
        logger.info("Auth: connected to MongoDB at %s", config.MONGODB_URI)
    except PyMongoError as exc:
        logger.warning(
            "Auth: MongoDB unreachable (%s). Falling back to local disk-based user storage.", exc
        )
        _repository = LocalAuthRepository(config.LOCAL_FALLBACK_DIR / "auth")
    return _repository
