import pytest
import yaml
from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.ingest import article_chunks, page_chunks, status_of
from repermit.knowledge import PUBLIC_PACK, load_pack
from repermit.llm import Citation, build_prompt, completed_payload
from repermit.retrieval import Retriever, add_passage, case_query, create_index, load_cards, load_sources, terms
from repermit.samples import sample_model
from repermit.state import CaseState
from tests.test_llm import FakeAssessor, review

ROWS = [
    ("DBC-2021:1", "DBC-2021", "p. 1", "all", "current", "fire separation wall between apartments"),
    ("LO-3-1999:1", "LO-3-1999", "Art. 4", "dm", "superseded", "old permit article wall"),
    ("LO-3-1999:2", "LO-3-1999", "Art. 14", "dm", "current", "approved drawings must not change wall"),
    ("TRAKHEES-CP-01:1", "TRAKHEES-CP-01", "p. 1", "trakhees", "current", "modification permit wall"),
    ("card:LAW6", "CARDS", "Law 6/2019", "all", "current", "dividing wall shared by owners"),
]


@pytest.fixture
def index(tmp_path):
    path = tmp_path / "index.sqlite"
    connection = create_index(path)
    for id_, source, reference, jurisdiction, status, text in ROWS:
        add_passage(connection, {"id": id_, "source": source, "reference": reference, "url": "http://x", "jurisdiction": jurisdiction, "status": status, "text": text})
    connection.commit()
    connection.close()
    return path


def found(retriever, query="wall", authority=None):
    return [item["id"] for item in retriever.search(query, authority)]


def test_register_and_cards_are_consistent():
    sources = load_sources()
    assert all(source["issuer"] and source["jurisdiction"] and "enabled" in source for source in sources.values())
    ids = [card["id"] for card in load_cards()]
    assert len(ids) == len(set(ids))
    assert all(card["reference"] and card["text"] and card["jurisdiction"] for card in load_cards())


def test_superseded_articles_are_not_returned(index):
    assert "LO-3-1999:1" not in found(Retriever(index), authority="dm")


def test_other_authority_is_filtered(index):
    results = found(Retriever(index), authority="dm")
    assert "LO-3-1999:2" in results
    assert "TRAKHEES-CP-01:1" not in results


def test_unknown_authority_gets_only_general_sources(index):
    assert set(found(Retriever(index))) == {"DBC-2021:1", "card:LAW6"}


def test_disabled_source_needs_no_rebuild(index, tmp_path):
    sources = load_sources()
    sources["DBC-2021"]["enabled"] = False
    path = tmp_path / "sources.yaml"
    path.write_text(yaml.safe_dump({"sources": list(sources.values())}), encoding="utf-8")
    assert "DBC-2021:1" not in found(Retriever(index, path))


def test_query_without_terms_returns_nothing(index):
    assert Retriever(index).search("a of", None) == []


def test_search_terms_cannot_inject_query_syntax(index):
    assert "OR" not in " ".join(terms('wall" OR NOT (x) *'))
    assert Retriever(index).search('wall" NEAR( ) *', None) == []


def test_case_query_uses_model_changes_and_questions():
    state = CaseState("c")
    state.modification = {"description": "Move a wall", "change_type": "modification", "facts": {}}
    state.evidence["m"] = [{"type": "design_model", "description": "m", "status": "current", "facts": {}, "changes": [{"name": "Wall 4A-4B"}]}]
    state.llm_review = {"information_requests": [{"question": "Who owns the unit?"}]}
    query = case_query(state)
    assert "Wall 4A-4B" in query and "Who owns" in query


def test_articles_are_split_and_marked_superseded():
    chunks = article_chunks("Intro\nArticle (4)\nOld text\nArticle (14)\nKept text\n")
    assert [reference for reference, _ in chunks] == ["Preamble", "Art. 4", "Art. 14"]
    source = {"superseded_articles": ["4"]}
    assert status_of("Art. 4", source) == "superseded"
    assert status_of("Art. 14", source) == "current"


def test_pages_keep_page_and_clause():
    assert page_chunks(["A.5.1 Existing buildings"])[0][0] == "p. 1, A.5.1"


PASSAGE = {"id": "card:LAW6", "source": "CARDS", "title": "Cards", "reference": "Law 6/2019", "url": "", "verified": False, "text": "x" * 500}


def test_invented_citation_is_removed_and_excerpt_is_short(pack):
    result = review()
    result.citations = [Citation(passage_id="card:LAW6", claim="Shared."), Citation(passage_id="fake", claim="No.")]
    payload = completed_payload(result, "B", "fake", pack, [PASSAGE])
    assert [item["passage_id"] for item in payload["citations"]] == ["card:LAW6"]
    assert payload["invalid_citations"] == ["fake"]
    assert len(payload["sources"][0]["excerpt"]) == 300
    assert "text" not in payload["sources"][0]


def test_prompt_carries_sources_as_data(pack):
    state = CaseState("c", revision="B")
    state.modification = {"description": "x", "change_type": None, "facts": {}}
    assert "card:LAW6" in build_prompt(state, pack, [PASSAGE]).split("<sources>")[1].split("</sources>")[0]


def delivered(client):
    case = client.post("/demo/scenarios/llm_free_text").json()
    return client.post(f"/cases/{case['case_id']}/models", content=sample_model("llm_free_text", "proposed")).json()


def test_review_receives_passages_and_records_them(database_url, index):
    assessor = FakeAssessor(review("modification"))
    client = TestClient(create_app(database_url, load_pack(PUBLIC_PACK), assessor, Retriever(index)))
    assert client.get("/meta").json()["knowledge_enabled"] is True
    case = delivered(client)
    assert assessor.passages
    assert {"id", "reference", "excerpt"} <= set(case["assessment"]["llm_review"]["sources"][0])


def test_passages_do_not_change_domains(database_url, index):
    assessor = FakeAssessor(review("modification"))
    with_sources = TestClient(create_app(database_url, load_pack(PUBLIC_PACK), assessor, Retriever(index)))
    without = TestClient(create_app(database_url, load_pack(PUBLIC_PACK), assessor))
    assert delivered(with_sources)["assessment"]["domains"] == delivered(without)["assessment"]["domains"]


def test_review_runs_without_an_index(database_url):
    client = TestClient(create_app(database_url, load_pack(PUBLIC_PACK), FakeAssessor(review("modification"))))
    assert delivered(client)["assessment"]["llm_review"]["sources"] == []
