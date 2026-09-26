"""Live API key verification.

Lets the user confirm, from inside the running app, that each configured
provider key actually authenticates - without needing to inspect logs or
round-trip through a third party. Each check is a single lightweight
"list models" call (no tokens generated, effectively free).
"""
import requests

from . import config

_TIMEOUT = 8

_ENDPOINTS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "params": lambda key: {"key": key},
    },
    "openai": {
        "url": "https://api.openai.com/v1/models",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
    },
}


def _mask(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 10:
        return key[:2] + "…"
    return f"{key[:6]}…{key[-4:]} ({len(key)} chars)"


def _api_key_for(provider: str) -> str:
    return {
        "groq": config.GROQ_API_KEY,
        "gemini": config.GEMINI_API_KEY,
        "openai": config.OPENAI_API_KEY,
    }.get(provider, "")


def verify_provider(provider: str) -> dict:
    key = _api_key_for(provider)
    if not key:
        return {"status": "missing", "detail": "No key configured in backend/.env.", "key_preview": None}

    endpoint = _ENDPOINTS[provider]
    kwargs = {"timeout": _TIMEOUT}
    if "headers" in endpoint:
        kwargs["headers"] = endpoint["headers"](key)
    if "params" in endpoint:
        kwargs["params"] = endpoint["params"](key)

    try:
        resp = requests.get(endpoint["url"], **kwargs)
    except requests.exceptions.RequestException as exc:
        return {
            "status": "network_error",
            "detail": f"Could not reach {provider}'s API from this server: {exc}",
            "key_preview": _mask(key),
        }

    if resp.status_code == 200:
        return {"status": "ok", "detail": "Key authenticated successfully.", "key_preview": _mask(key)}
    if resp.status_code in (401, 403):
        return {
            "status": "invalid",
            "detail": f"Provider rejected this key ({resp.status_code}): {resp.text[:200]}",
            "key_preview": _mask(key),
        }
    return {
        "status": "error",
        "detail": f"Unexpected response ({resp.status_code}): {resp.text[:200]}",
        "key_preview": _mask(key),
    }


def verify_all_providers() -> dict:
    return {provider: verify_provider(provider) for provider in _ENDPOINTS}
