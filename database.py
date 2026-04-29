from typing import Generator

from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

from settings import get_settings


settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _ensure_sqlite_schema()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def _ensure_sqlite_schema() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    expected_columns = {
        "attendance_messages": {
            "source_checklists": "TEXT",
            "source_normative": "TEXT",
            "answer_source": "VARCHAR",
            "fallback_contact": "BOOLEAN DEFAULT 1",
            "knowledge_base_used": "BOOLEAN DEFAULT 0",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in expected_columns.items():
            existing = {
                row[1]
                for row in connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
            }
            if not existing:
                continue

            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
