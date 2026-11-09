from tests.test_documents import PACK, Case, codes

TYPE, SPEC = next((name, spec) for name, spec in PACK.documents.items() if spec.proves)
FACT = SPEC.proves[0]


def decide(case, role="authority", present=None, facts=None, note="Checked page 2."):
    body = {
        "evidence_id": f"{TYPE}-B",
        "present": SPEC.must_contain if present is None else present,
        "facts": facts if facts is not None else {FACT: "yes"},
        "note": note,
        "actor_id": "reviewer-1",
        "role": role,
    }
    return case.client.post(f"/cases/{case.id}/document-decisions", json=body)


def test_reviewer_completes_a_document_without_a_call(database_url):
    case = Case(database_url)
    case.upload(TYPE)
    calls = case.assessor.calls
    response = decide(case)
    assert response.status_code == 200, response.text
    data = response.json()
    verdict = next(item for item in data["document_verdicts"] if item["evidence_id"] == f"{TYPE}-B")
    assert verdict["status"] == "complete" and verdict["assessed_by"] == "reviewer"
    assert FACT not in codes(data) and TYPE not in codes(data)
    assert any(item["type"] == "confirmed_fact" and item["facts"] == {FACT: True} for item in data["evidence"])
    assert case.assessor.calls == calls


def test_reviewer_marks_a_document_incomplete(database_url):
    case = Case(database_url)
    case.upload(TYPE)
    data = decide(case, present=SPEC.must_contain[1:], facts={}, note="The stamp is missing.").json()
    assert codes(data).get(TYPE) == "document_incomplete"
    verdict = next(item for item in data["document_verdicts"] if item["evidence_id"] == f"{TYPE}-B")
    assert verdict["missing"] == SPEC.must_contain[:1] and verdict["problems"] == ["The stamp is missing."]


def test_only_a_reviewer_may_assess(database_url):
    case = Case(database_url)
    case.upload(TYPE)
    assert decide(case, role="consultant").status_code == 403
    history = case.client.get(f"/cases/{case.id}/history").json()
    assert history[-1]["type"] == "resolution_denied"
    assert all(item["evidence_id"] != f"{TYPE}-B" for item in case.state()["document_verdicts"])


def test_facts_must_be_proven_by_a_complete_document(database_url):
    case = Case(database_url)
    case.upload(TYPE)
    other = next(name for name in PACK.facts if name not in SPEC.proves)
    assert decide(case, facts={other: "yes"}).status_code == 422
    assert decide(case, present=[], facts={FACT: "yes"}).status_code == 422
    assert decide(case, present=["not on the checklist"]).status_code == 422


def test_the_original_file_is_kept_and_can_be_opened(database_url):
    from repermit.samples import sample_document

    case = Case(database_url)
    content = sample_document("llm_free_text", TYPE)
    case.upload(TYPE, content)
    item = next(item for item in case.state()["evidence"] if item["evidence_id"] == f"{TYPE}-B")
    assert item["file_kept"] is True
    response = case.client.get(f"/cases/{case.id}/documents/{TYPE}-B/file", params={"version": 1})
    assert response.status_code == 200 and response.content == content
    assert response.headers["content-type"] == "application/pdf" and "inline" in response.headers["content-disposition"]


def test_each_version_keeps_its_own_file(database_url):
    from repermit.samples import sample_document

    case = Case(database_url)
    first, second = sample_document("llm_free_text", TYPE), sample_document("llm_free_text", TYPE, incomplete=True)
    case.upload(TYPE, first)
    case.upload(TYPE, second)
    url = f"/cases/{case.id}/documents/{TYPE}-B/file"
    assert case.client.get(url, params={"version": 1}).content == first
    assert case.client.get(url).content == second


def test_a_file_that_was_not_kept_is_reported(database_url):
    from sqlalchemy import delete

    from repermit.store import document_files

    case = Case(database_url)
    case.upload(TYPE)
    with case.client.app.state.store.engine.begin() as connection:
        connection.execute(delete(document_files))
    item = next(item for item in case.state()["evidence"] if item["evidence_id"] == f"{TYPE}-B")
    assert item["file_kept"] is False
    response = case.client.get(f"/cases/{case.id}/documents/{TYPE}-B/file")
    assert response.status_code == 404 and "not kept" in response.json()["detail"]
    assert case.client.get(f"/cases/{case.id}/documents/nope/file").status_code == 404


def test_unknown_document_is_not_found(database_url):
    case = Case(database_url)
    body = {"evidence_id": "nope", "present": [], "facts": {}, "actor_id": "r", "role": "authority"}
    assert case.client.post(f"/cases/{case.id}/document-decisions", json=body).status_code == 404
