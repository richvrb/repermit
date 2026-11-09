"""Append-only event store. Events are the only persisted case state."""

from sqlalchemy import JSON, Column, Integer, LargeBinary, MetaData, String, Table, create_engine, insert, select, text
from sqlalchemy.exc import IntegrityError

metadata = MetaData()

case_events = Table(
    "case_events",
    metadata,
    Column("case_id", String(36), primary_key=True),
    Column("seq", Integer, primary_key=True, autoincrement=False),
    Column("type", String(64), nullable=False),
    Column("at", String(40), nullable=False),
    Column("payload", JSON, nullable=False),
)


# Uploaded document files, by the SHA-256 the evidence records, so the original can be opened and verified.
document_files = Table(
    "document_files",
    metadata,
    Column("sha256", String(64), primary_key=True),
    Column("content", LargeBinary, nullable=False),
)

# Each change of the AI settings is a new row, so the history shows who changed what.
settings_changes = Table(
    "settings_changes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("at", String(40), nullable=False),
    Column("actor_id", String(100), nullable=False),
    Column("role", String(40), nullable=False),
    Column("settings", JSON, nullable=False),
)


class ConcurrentWrite(Exception):
    """Another write already used this event sequence number."""


class EventStore:
    def __init__(self, url: str):
        self.engine = create_engine(url, pool_pre_ping=True)
        metadata.create_all(self.engine)

    def load(self, case_id: str) -> list[dict]:
        query = select(case_events).where(case_events.c.case_id == case_id).order_by(case_events.c.seq)
        with self.engine.connect() as connection:
            return [dict(row._mapping) for row in connection.execute(query)]

    def case_ids(self) -> list[str]:
        """All cases, newest first."""
        query = select(case_events.c.case_id).where(case_events.c.seq == 1).order_by(case_events.c.at.desc())
        with self.engine.connect() as connection:
            return [row.case_id for row in connection.execute(query)]

    def llm_cost_since(self, since: str) -> float:
        """Cost of all LLM calls recorded at or after an ISO timestamp, across cases."""
        paid = ("llm_review_recorded", "llm_documents_read")
        query = select(case_events.c.payload).where(case_events.c.type.in_(paid), case_events.c.at >= since)
        with self.engine.connect() as connection:
            return sum((row.payload.get("usage") or {}).get("cost_usd") or 0.0 for row in connection.execute(query))

    def append(self, case_id: str, events: list[dict]) -> None:
        if not events:
            return
        try:
            with self.engine.begin() as connection:
                connection.execute(insert(case_events), [{"case_id": case_id, **event} for event in events])
        except IntegrityError as error:
            raise ConcurrentWrite(case_id) from error

    def save_file(self, sha256: str, content: bytes) -> None:
        """Stores a file once; the same content uploaded again is already there."""
        with self.engine.begin() as connection:
            if connection.execute(select(document_files.c.sha256).where(document_files.c.sha256 == sha256)).first() is None:
                connection.execute(insert(document_files), [{"sha256": sha256, "content": content}])

    def load_file(self, sha256: str) -> bytes | None:
        with self.engine.connect() as connection:
            row = connection.execute(select(document_files.c.content).where(document_files.c.sha256 == sha256)).first()
        return row.content if row else None

    def stored_files(self, hashes: set[str]) -> set[str]:
        if not hashes:
            return set()
        with self.engine.connect() as connection:
            return {row.sha256 for row in connection.execute(select(document_files.c.sha256).where(document_files.c.sha256.in_(hashes)))}

    def save_settings(self, settings: dict, actor_id: str, role: str, at: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(insert(settings_changes), [{"at": at, "actor_id": actor_id, "role": role, "settings": settings}])

    def settings_history(self, limit: int = 20) -> list[dict]:
        """Newest first."""
        query = select(settings_changes).order_by(settings_changes.c.id.desc()).limit(limit)
        with self.engine.connect() as connection:
            return [dict(row._mapping) for row in connection.execute(query)]

    def ping(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
