import re

import bcrypt
from fastapi import Header, HTTPException

from .auth_db import get_auth_repository

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def register(email: str, password: str) -> tuple[dict, str]:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Please enter a valid email address.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    repo = get_auth_repository()
    user = repo.create_user(email, _hash_password(password))
    token = repo.create_session(user["id"])
    return user, token


def login(email: str, password: str) -> tuple[dict, str]:
    email = email.strip().lower()
    repo = get_auth_repository()
    user_doc = repo.get_user_by_email(email)
    if not user_doc or not _verify_password(password, user_doc["password_hash"]):
        raise ValueError("Invalid email or password.")

    user_id = str(user_doc["_id"]) if "_id" in user_doc else user_doc["id"]
    token = repo.create_session(user_id)
    user = repo.get_user_by_id(user_id)
    return user, token


def logout(token: str) -> None:
    if not token:
        return
    get_auth_repository().delete_session(token)


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return authorization.split(" ", 1)[1].strip()


def get_current_user(authorization: str | None = Header(None)) -> dict:
    token = _extract_token(authorization)
    repo = get_auth_repository()
    user_id = repo.get_session_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please sign in again.")
    return user


def get_current_token(authorization: str | None = Header(None)) -> str:
    return _extract_token(authorization)
