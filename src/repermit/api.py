"""HTTP API."""

import os
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from repermit.bim import MAX_MODEL_BYTES
from repermit.demo import catalog, start_scenario
from repermit.knowledge import PUBLIC_PACK, Pack, load_pack
from repermit.llm import MODEL, Assessor, ClaudeAssessor
from repermit.samples import sample_model
from repermit.service import ActionForbidden, ActionHeld, CaseNotFound, CaseService, InvalidRequest, UnknownItem
from repermit.store import ConcurrentWrite, EventStore

Fact = bool | int | float | str
STATIC_DIR = Path(__file__).parent / "static"


class CaseRequest(BaseModel):
    project_name: str
    revision: str
    responsible_role: str
    permit_type: Literal["modification", "new_permit"] = "modification"


class ModificationRequest(BaseModel):
    revision: str
    change_type: str | None = None
    description: str
    facts: dict[str, Fact] = {}


class EvidenceRequest(BaseModel):
    evidence_id: str
    category: Literal["document", "assessment", "approval"]
    type: str
    domain: str
    status: Literal["current", "incomplete", "superseded", "withdrawn"] = "current"
    revision: str | None = None
    format: str | None = None
    description: str | None = None
    valid_until: date | None = None
    facts: dict[str, Fact] = {}


class Answer(BaseModel):
    question: str
    answer: str


class ResponseRequest(BaseModel):
    facts: dict[str, Fact] = {}
    answers: list[Answer] = []
    documents: list[str] = []
    note: str | None = None


class ActionRequest(BaseModel):
    action: str
    actor_id: str
    role: str


class ResolutionRequest(BaseModel):
    issue_id: str
    actor_id: str
    role: str
    source: str
    decision: str
    selected_rule_id: str | None = None


ERROR_STATUS = {
    CaseNotFound: 404,
    UnknownItem: 404,
    InvalidRequest: 422,
    ActionForbidden: 403,
    ActionHeld: 409,
    ConcurrentWrite: 409,
}


def create_app(database_url: str, pack: Pack, assessor: Assessor | None = None) -> FastAPI:
    app = FastAPI(title="RePermit", version="0.1.0")
    store = EventStore(database_url)
    synthetic = load_pack()
    packs = {synthetic.version: synthetic, pack.version: pack}
    service = CaseService(store, pack, assessor=assessor, packs=packs)
    offline_service = CaseService(store, synthetic, packs=packs)
    app.state.store = store

    async def handle_error(_: Request, error: Exception) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=ERROR_STATUS[type(error)])

    for error_type in ERROR_STATUS:
        app.add_exception_handler(error_type, handle_error)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/meta")
    def meta():
        return {
            "pack_version": pack.version,
            "llm_enabled": assessor is not None,
            "llm_model": assessor.model if assessor else None,
            "roles": pack.roles,
            "stages": pack.stages,
            "resolution_roles": pack.resolution_roles,
        }

    @app.get("/demo/scenarios")
    def demo_scenarios():
        return [{**scenario, "available": assessor is not None or not scenario["live"]} for scenario in catalog()]

    @app.post("/demo/scenarios/{scenario_id}", status_code=201)
    def start_demo_scenario(scenario_id: str):
        return start_scenario(scenario_id, offline_service, service)

    @app.get("/demo/models/{scenario_id}/{kind}")
    def demo_model(scenario_id: str, kind: str):
        headers = {"Content-Disposition": f'attachment; filename="{scenario_id}-{kind}.ifc"'}
        return Response(sample_model(scenario_id, kind), media_type="application/x-step", headers=headers)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        try:
            store.ping()
        except SQLAlchemyError:
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return {"status": "ready", "pack_version": pack.version}

    @app.post("/cases", status_code=201)
    def open_case(request: CaseRequest):
        return service.open_case(request.project_name, request.revision, request.responsible_role, request.permit_type)

    @app.get("/cases")
    def list_cases():
        return service.list_cases()

    @app.get("/cases/{case_id}")
    def get_case(case_id: str, at: int | None = None):
        return service.get_case(case_id, at)

    @app.get("/cases/{case_id}/history")
    def get_history(case_id: str):
        return [
            {**event, "payload": {key: value for key, value in event["payload"].items() if key != "elements"}}
            for event in service.get_history(case_id)
        ]

    @app.post("/cases/{case_id}/modifications")
    def submit_modification(case_id: str, request: ModificationRequest):
        return service.submit_modification(case_id, request.model_dump())

    @app.post("/cases/{case_id}/llm-review")
    def rerun_review(case_id: str):
        return service.rerun_review(case_id)

    @app.post("/cases/{case_id}/evidence")
    def register_evidence(case_id: str, request: EvidenceRequest):
        return service.register_evidence(case_id, request.model_dump(mode="json"))

    @app.post("/cases/{case_id}/models")
    async def upload_model(case_id: str, request: Request, kind: Literal["baseline", "proposed"] = "proposed", filename: str = "model.ifc"):
        if int(request.headers.get("content-length", 0)) > MAX_MODEL_BYTES:
            raise InvalidRequest("the model is larger than 50 MB")
        content = await request.body()
        return await run_in_threadpool(service.register_model, case_id, kind, filename, content)

    @app.post("/cases/{case_id}/responses")
    def submit_response(case_id: str, request: ResponseRequest):
        return service.submit_response(case_id, request.model_dump())

    @app.post("/cases/{case_id}/actions")
    def request_action(case_id: str, request: ActionRequest):
        return service.request_action(case_id, request.action, request.actor_id, request.role)

    @app.post("/cases/{case_id}/resolutions")
    def resolve_issue(case_id: str, request: ResolutionRequest):
        resolution = request.model_dump(exclude={"issue_id"})
        return service.resolve_issue(case_id, request.issue_id, resolution)

    return app


def app_from_env() -> FastAPI:
    database_url = os.environ.get("REPERMIT_DATABASE_URL", "sqlite:///repermit.db")
    pack = load_pack(os.environ.get("REPERMIT_PACK_PATH", PUBLIC_PACK))
    assessor = None
    if os.environ.get("REPERMIT_LLM_PROVIDER", "anthropic") != "none":
        assessor = ClaudeAssessor(os.environ.get("REPERMIT_LLM_MODEL", MODEL))
    return create_app(database_url, pack, assessor)
