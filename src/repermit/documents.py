"""Document evidence: reading PDFs, and judging them against the checklist of their type."""

import hashlib
import io

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from repermit.knowledge import Pack
from repermit.state import CaseState

MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
MAX_TEXT_CHARS = 40000


class InvalidDocument(Exception):
    pass


def read_document(content: bytes) -> dict:
    """Parse a PDF. A scan has no text layer, which counts as unreadable."""
    if len(content) > MAX_DOCUMENT_BYTES:
        raise InvalidDocument("the document is larger than 20 MB")
    if not content.startswith(b"%PDF-"):
        raise InvalidDocument("the file is not a PDF")
    try:
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except (PyPdfError, ValueError, TypeError, KeyError) as error:
        raise InvalidDocument(f"the PDF could not be read: {error}") from error
    if not text:
        raise InvalidDocument("the PDF has no readable text, for example because it is a scan")
    return {
        "document": {"sha256": hashlib.sha256(content).hexdigest(), "size": len(content), "pages": len(reader.pages)},
        "text": text[:MAX_TEXT_CHARS],
    }


def coerce(value: str):
    lowered = value.strip().lower()
    return {"true": True, "yes": True, "false": False, "no": False}.get(lowered, value.strip())


def judge(item: dict, review: dict, pack: Pack) -> dict:
    """The LLM reports; this decides. An item that is not reported as present is missing."""
    spec = pack.documents[item["type"]]
    present = {entry["item"] for entry in review["checklist"] if entry["present"]}
    missing = [entry for entry in spec.must_contain if entry not in present]
    problems = list(review["problems"])
    if not review["is_expected_type"]:
        problems.insert(0, "This is not the requested type of document.")
    if not review["matches_case"]:
        problems.insert(0, "This document does not match this case or revision.")
    complete = review["is_expected_type"] and review["matches_case"] and not missing
    facts = [fact for fact in review["extracted_facts"] if fact["name"] in spec.proves] if complete else []
    return {
        "evidence_id": item["evidence_id"],
        "version": item["version"],
        "type": item["type"],
        "status": "complete" if complete else "incomplete",
        "missing": missing,
        "problems": problems,
        "checklist": review["checklist"],
        "facts": [{**fact, "value": coerce(fact["value"])} for fact in facts],
    }


def judge_reviews(reviews: list[dict], state: CaseState, pack: Pack) -> list[dict]:
    latest = {item["evidence_id"]: item for item in state.latest_evidence() if item["type"] in pack.documents}
    return [judge(latest[review["evidence_id"]], review, pack) for review in reviews if review["evidence_id"] in latest]
