"""Append-only event store. Events are the only persisted case state."""

from sqlalchemy import JSON, Column, Integer, MetaData, String, Table, create_engine, insert, select, text
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

    def append(self, case_id: str, events: list[dict]) -> None:
        if not events:
            return
        try:
            with self.engine.begin() as connection:
                connection.execute(insert(case_events), [{"case_id": case_id, **event} for event in events])
        except IntegrityError as error:
            raise ConcurrentWrite(case_id) from error

    def ping(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
