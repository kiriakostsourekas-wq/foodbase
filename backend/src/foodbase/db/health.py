from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from foodbase.db.session import get_engine


def check_database_health() -> tuple[bool, str | None]:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("select 1"))
    except (SQLAlchemyError, ValueError) as exc:
        return False, str(exc)

    return True, None
