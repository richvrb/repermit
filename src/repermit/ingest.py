"""Download the registered sources and build the search index in knowledge/.

Run with: python -m repermit.ingest
The folder stays out of git and the image: reuse terms limit it to internal use.
"""

import io
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

from repermit.retrieval import CARD_SOURCE, add_passage, create_index, load_cards, load_sources

KNOWLEDGE = Path("knowledge")
CHUNK_CHARS = 1400
ARTICLE = re.compile(r"^\s*Article\s*\(?(\d+)\)?", re.I | re.M)
CLAUSE = re.compile(r"\b([A-K]\.\d+(?:\.\d+){0,3})\b")


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
        if tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(content: bytes) -> str:
    parser = TextOnly()
    parser.feed(content.decode("utf-8", errors="replace"))
    return re.sub(r"[ \t\xa0]+", " ", "".join(parser.parts))


def pdf_pages(content: bytes) -> list[str]:
    return [page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages]


def split(text: str) -> list[str]:
    """Paragraph-sized pieces up to the chunk size."""
    chunks, current = [], ""
    for paragraph in re.split(r"\n\s*\n|\n(?=[A-Z(])", text):
        paragraph = paragraph.strip()
        if current and len(current) + len(paragraph) > CHUNK_CHARS:
            chunks.append(current)
            current = ""
        current = f"{current}\n{paragraph}".strip()
        while len(current) > CHUNK_CHARS * 1.5:
            chunks.append(current[:CHUNK_CHARS])
            current = current[CHUNK_CHARS:]
    return chunks + ([current] if current.strip() else [])


def article_chunks(text: str) -> list[tuple[str, str]]:
    """Legislation: chunks per article, with the article number as reference."""
    marks = list(ARTICLE.finditer(text))
    pieces = [("Preamble", text[:marks[0].start()] if marks else text)]
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        pieces.append((f"Art. {mark.group(1)}", text[mark.start():end]))
    return [(reference, chunk) for reference, body in pieces for chunk in split(body)]


def page_chunks(pages: list[str]) -> list[tuple[str, str]]:
    """Long documents: chunks per page, with the first clause number when there is one."""
    chunks = []
    for number, page in enumerate(pages, 1):
        for chunk in split(page):
            clause = CLAUSE.search(chunk)
            chunks.append((f"p. {number}" + (f", {clause.group(1)}" if clause else ""), chunk))
    return chunks


def status_of(reference: str, source: dict) -> str:
    return "superseded" if reference.removeprefix("Art. ") in source.get("superseded_articles", []) else "current"


def fetch(source: dict, folder: Path) -> bytes:
    suffix = ".pdf" if source["url"].lower().endswith(".pdf") else ".html"
    path = folder / f"{source['id']}{suffix}"
    if not path.exists():
        request = urllib.request.Request(source["url"], headers={"User-Agent": "Mozilla/5.0 RePermit research"})
        with urllib.request.urlopen(request, timeout=180) as response:
            path.write_bytes(response.read())
    return path.read_bytes()


def chunks_of(source: dict, content: bytes) -> list[tuple[str, str]]:
    if content[:5] == b"%PDF-":
        pages = pdf_pages(content)
        return page_chunks(pages) if len(pages) > 25 else article_chunks("\n".join(pages))
    if b"<html" not in content[:2000].lower() and b"<!doctype" not in content[:2000].lower():
        raise ValueError("neither a PDF nor an HTML page")
    return article_chunks(html_text(content))


def add_cards(connection) -> int:
    cards = load_cards()
    for card in cards:
        add_passage(connection, {
            "id": f"card:{card['id']}", "source": CARD_SOURCE, "reference": card["reference"], "url": card["url"],
            "jurisdiction": card["jurisdiction"], "status": "current", "text": f"{card['reference']}. {card['text']}",
        })
    return len(cards)


def build(folder: Path = KNOWLEDGE) -> None:
    raw = folder / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    connection = create_index(folder / "index.sqlite")
    print(f"{'cards':20} {add_cards(connection)} passages")
    for source in load_sources().values():
        if source["id"] == CARD_SOURCE:
            continue
        try:
            chunks = chunks_of(source, fetch(source, raw))
        except (OSError, ValueError) as error:
            print(f"{source['id']:20} FAILED: {error}")
            continue
        for index, (reference, text) in enumerate(chunks):
            add_passage(connection, {
                "id": f"{source['id']}:{index}", "source": source["id"], "reference": reference, "url": source["url"],
                "jurisdiction": source["jurisdiction"], "status": status_of(reference, source), "text": text,
            })
        print(f"{source['id']:20} {len(chunks)} passages")
    connection.commit()
    connection.close()


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else KNOWLEDGE)
