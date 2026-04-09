from pydantic import SecretStr

from foodbase.config import Settings


def test_builds_database_url_from_password_only_configuration() -> None:
    settings = Settings(
        _env_file=None,
        database_url=None,
        db_password=SecretStr("test-password"),
        db_host="db.example.supabase.co",
        db_port=5432,
        db_name="postgres",
        db_user="postgres",
        db_sslmode="require",
    )

    assert (
        settings.sqlalchemy_database_url
        == "postgresql+psycopg://postgres:test-password@db.example.supabase.co:5432/postgres?sslmode=require"
    )


def test_database_url_override_is_normalized_for_sqlalchemy() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql://user:pass@example.com:5432/postgres",
    )

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@example.com:5432/postgres"
