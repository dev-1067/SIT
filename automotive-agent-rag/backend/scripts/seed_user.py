"""Ek demo login account seed karta hai (jis DB se backend/.env connect hai usi mein).

Usage:
    cd backend
    source .venv/bin/activate   # ya jo bhi venv activate karte ho
    python scripts/seed_user.py [email] [password]

Agar email/password nahi diya to default dev@sit.com / dev-sit use hota hai.
Agar account pehle se hai to bas skip kar dega (error nahi dega).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import auth  # noqa: E402


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else "dev@sit.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "dev-sit"

    try:
        user, _token = auth.register(email, password)
        print(f"Account ban gaya: {user['email']} (id: {user['id']})")
    except ValueError as exc:
        if "already exists" in str(exc):
            print(f"Account pehle se maujood hai: {email} — kuch nahi kiya, seedha login kar sakte ho.")
        else:
            print(f"Error: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
