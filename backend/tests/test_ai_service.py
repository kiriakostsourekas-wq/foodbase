from fastapi import HTTPException
from pydantic import SecretStr

from foodbase.ai import service
from foodbase.config import Settings


def test_get_groq_client_rejects_blank_api_key(monkeypatch) -> None:
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: Settings(_env_file=None, groq_api_key=SecretStr("   ")),
    )

    try:
        service._get_groq_client()
    except HTTPException as exc:
        assert exc.status_code == 503
        assert "FOODBASE_GROQ_API_KEY" in exc.detail
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("Expected HTTPException for blank Groq API key")
