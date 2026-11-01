from sqlalchemy.exc import OperationalError


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_reports_pack_version(client):
    assert client.get("/ready").json() == {"status": "ready", "pack_version": "synthetic-2026.1"}


def test_ready_fails_when_database_is_down(client, monkeypatch):
    def fail():
        raise OperationalError("SELECT 1", {}, Exception("down"))

    monkeypatch.setattr(client.app.state.store, "ping", fail)
    assert client.get("/ready").status_code == 503


def test_unknown_case_is_not_found(client):
    assert client.get("/cases/nope").status_code == 404
    assert client.get("/cases/nope/history").status_code == 404


def test_unknown_role_creates_no_case(client):
    body = {"project_name": "x", "revision": "A", "responsible_role": "wizard"}
    assert client.post("/cases", json=body).status_code == 422


def test_modification_requires_new_revision(api):
    api.open()
    body = {"revision": "A", "change_type": "wall_relocation", "description": "x"}
    assert api.client.post(f"/cases/{api.case_id}/modifications", json=body).status_code == 422
    assert api.history_types() == ["case_opened"]


def test_evidence_versions_are_retained(api):
    api.open()
    api.evidence("doc", "floor_plan", "architectural", revision="A")
    case = api.evidence("doc", "floor_plan", "architectural", revision="B")
    assert [item["version"] for item in case["evidence"]] == [2]
    assert api.history_types().count("evidence_registered") == 2


def bim_evidence(format=None):
    return {
        "evidence_id": "model", "category": "document", "type": "design_model",
        "domain": "architectural", "revision": "A", "format": format,
    }


def open_new_permit(client):
    body = {"project_name": "x", "revision": "A", "responsible_role": "consultant", "permit_type": "new_permit"}
    return client.post("/cases", json=body).json()["case_id"]


def test_new_permit_rejects_other_or_missing_format(client):
    case_id = open_new_permit(client)
    for format in ("pdf", None):
        response = client.post(f"/cases/{case_id}/evidence", json=bim_evidence(format))
        assert response.status_code == 422
        assert "ifc" in response.text
    assert len(client.get(f"/cases/{case_id}/history").json()) == 1


def test_modification_case_accepts_pdf(api):
    api.open()
    response = api.client.post(f"/cases/{api.case_id}/evidence", json=bim_evidence("pdf"))
    assert response.status_code == 200


def test_unknown_action_and_issue_are_not_found(api):
    api.open()
    assert api.act("fly").status_code == 404
    assert api.resolve("gap:none").status_code == 404
