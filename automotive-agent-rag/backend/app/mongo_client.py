"""Shared MongoDB connection helper.

Some environments (notably certain Python/Windows setups reaching MongoDB
Atlas) fail TLS validation against the system's default CA store. Retrying
once with certifi's CA bundle fixes that without weakening verification.
"""
from pymongo import MongoClient


def connect(uri: str, timeout_ms: int = 5000) -> MongoClient:
    last_err = None
    for use_certifi in (False, True):
        kwargs = {"serverSelectionTimeoutMS": timeout_ms}
        if use_certifi:
            try:
                import certifi

                kwargs["tlsCAFile"] = certifi.where()
            except ImportError:
                continue
        try:
            client = MongoClient(uri, **kwargs)
            client.admin.command("ping")
            return client
        except Exception as err:  # noqa: BLE001
            last_err = err
            continue
    raise last_err
