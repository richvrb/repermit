"""Retrieval of source passages for LLM reviews. Passages advise; rules and evidence decide."""

import re
import sqlite3
from pathlib import Path

import yaml

from repermit.assessment import collect_facts
from repermit.state import CaseState

PACKS = Path(__file__).parent / "packs"
SOURCES = PACKS / "sources.yaml"
CARDS = PACKS / "cards.yaml"
CARD_SOURCE = "CARDS"
MAX_PER_SOURCE = 3
CANDIDATES = 80
MAX_TERMS = 40
EXCERPT_CHARS = 300
# A passage must score near the best one and share enough terms with the query.
CARD_LIMITS = {"total": 3, "relative": 0.5, "matched": 2}
PASSAGE_LIMITS = {"total": 5, "relative": 0.7, "matched": 3}
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "will", "have", "has", "not", "our", "their",
    "want", "into", "any", "all", "out", "its", "but", "can", "does", "new", "existing", "which", "what", "there",
    "who", "when", "how", "may", "must", "need", "needed", "required", "between", "without", "per", "same", "they",
    "you", "your", "been", "over", "these", "those", "about", "than", "then", "also", "only", "such", "under",
}


def load_sources(path: Path = SOURCES) -> dict[str, dict]:
    with open(path, encoding="utf-8") as handle:
        return {source["id"]: source for source in yaml.safe_load(handle)["sources"]}


def load_cards(path: Path = CARDS) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)["cards"]


def create_index(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("DROP TABLE IF EXISTS passages")
    connection.execute(
        "CREATE VIRTUAL TABLE passages USING fts5("
        "id UNINDEXED, source UNINDEXED, reference UNINDEXED, url UNINDEXED, jurisdiction UNINDEXED, status UNINDEXED, "
        "text, tokenize='porter unicode61')"
    )
    return connection


def add_passage(connection: sqlite3.Connection, passage: dict) -> None:
    connection.execute(
        "INSERT INTO passages VALUES (:id, :source, :reference, :url, :jurisdiction, :status, :text)", passage,
    )


def terms(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9]{2,}", text.lower())
    return list(dict.fromkeys(word for word in words if word not in STOPWORDS))[:MAX_TERMS]


def case_query(state: CaseState) -> str:
    """Search text: the description, the type, what the model changed and what is still open."""
    modification = state.modification
    parts = [modification["description"], str(modification["change_type"]).replace("_", " ")]
    for item in state.latest_evidence():
        parts += [change["name"] for change in item.get("changes", [])]
        parts += [item["description"] or ""] if item["type"] == "note" else []
    review = state.llm_review or {}
    parts += [request["question"] for request in review.get("information_requests", [])]
    return " ".join(parts)


def excerpt(passage: dict) -> dict:
    """What an event keeps of a passage: enough to trace it, not the full text."""
    return {**{key: value for key, value in passage.items() if key != "text"}, "excerpt": passage["text"][:EXCERPT_CHARS]}


class Retriever:
    def __init__(self, index: Path | str, sources_path: Path = SOURCES):
        self.index = Path(index)
        self.sources_path = sources_path

    def search(self, query: str, authority: str | None) -> list[dict]:
        words = terms(query)
        if not words:
            return []
        # Read per search, so switching off a source needs no rebuild.
        sources = load_sources(self.sources_path)
        match = " OR ".join(f'"{word}"' for word in words)
        connection = sqlite3.connect(f"{self.index.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
        try:
            # Cards are ranked apart: they are short, and the 843-page code would crowd them out.
            cards = self._ranked(connection, match, "source = ?", sources, authority, words, CARD_LIMITS)
            passages = self._ranked(connection, match, "source != ?", sources, authority, words, PASSAGE_LIMITS)
        finally:
            connection.close()
        return cards + passages

    def _ranked(self, connection, match: str, where: str, sources: dict, authority, words: list[str], limits: dict) -> list[dict]:
        rows = connection.execute(
            "SELECT id, source, reference, url, jurisdiction, status, text, -bm25(passages) FROM passages "
            f"WHERE passages MATCH ? AND {where} ORDER BY bm25(passages) LIMIT ?",
            (f"text : ({match})", CARD_SOURCE, CANDIDATES),
        ).fetchall()
        kept, per_source, best = [], {}, None
        needed = min(limits["matched"], len(words))
        for id_, source, reference, url, jurisdiction, status, text, score in rows:
            entry = sources.get(source)
            if entry is None or not entry["enabled"] or status != "current" or jurisdiction not in ("all", authority):
                continue
            best = best or score
            lowered = text.lower()
            if score < limits["relative"] * best or sum(word[:6] in lowered for word in words) < needed:
                continue
            if len(kept) < limits["total"] and per_source.get(source, 0) < MAX_PER_SOURCE:
                per_source[source] = per_source.get(source, 0) + 1
                kept.append({
                    "id": id_, "source": source, "title": entry["title"], "reference": reference, "url": url,
                    "verified": False, "text": text,
                })
        return kept

    def for_case(self, state: CaseState) -> list[dict]:
        authority = collect_facts(state)[0].get("competent_entity")
        return self.search(case_query(state), authority)
