"""HTTP API."""

import os
from collections.abc import Callable
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
from repermit.documents import MAX_DOCUMENT_BYTES
from repermit.knowledge import ARCHIVED_PACKS, PUBLIC_PACK, Pack, load_pack
from repermit.llm import MODEL, Assessor, ClaudeAssessor, DocumentReader
from repermit.retrieval import Retriever, load_cards, load_sources, terms
from repermit.samples import sample_document, sample_model
from repermit.service import BULKY, ActionForbidden, ActionHeld, CaseNotFound, CaseService, InvalidRequest, UnknownItem
from repermit.settings import DEFAULT_MODELS, AISettings
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


class FactDecision(BaseModel):
    name: str
    accepted: bool
    actor_id: str
    role: str


class DocumentDecision(BaseModel):
    evidence_id: str
    present: list[str] = []
    facts: dict[str, Fact] = {}
    note: str | None = None
    actor_id: str
    role: str


class SettingsRequest(BaseModel):
    review_model: str | None
    review_effort: str | None
    documents_model: str | None = None
    documents_effort: str = "medium"
    review_tool_calls: int | None = None
    case_budget_usd: float
    daily_budget_usd: float
    retrieval_enabled: bool | None = None
    retrieval_passages: int | None = None
    retrieval_cards: int | None = None
    actor_id: str
    role: str


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


def create_app(
    database_url: str,
    pack: Pack,
    assessor: Assessor | None = None,
    retriever: Retriever | None = None,
    case_budget_usd: float | None = None,
    daily_budget_usd: float | None = None,
    document_reader: DocumentReader | None = None,
    assessor_factory: Callable[[str, str], object] | None = None,
    allowed_models: tuple[str, ...] = DEFAULT_MODELS,
) -> FastAPI:
    app = FastAPI(title="RePermit", version="0.1.0")
    store = EventStore(database_url)
    synthetic = load_pack()
    packs = {item.version: item for item in [synthetic, *map(load_pack, ARCHIVED_PACKS), pack]}
    service = CaseService(
        store, pack, assessor=assessor, packs=packs, retriever=retriever,
        case_budget_usd=case_budget_usd, daily_budget_usd=daily_budget_usd, document_reader=document_reader,
    )
    settings = AISettings(service, store, assessor_factory, allowed_models)
    settings.restore()

    def task(worker) -> dict | None:
        return {"model": worker.model, "effort": getattr(worker, "effort", None)} if worker else None

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
            "llm_enabled": service.assessor is not None,
            "llm_model": service.assessor.model if service.assessor else None,
            "knowledge_enabled": retriever is not None and retriever.enabled,
            # Per AI task; documents is None when the review reads documents itself.
            "ai": {"review": task(service.assessor), "documents": task(service.document_reader) if service.assessor else None},
            "case_budget_usd": service.case_budget_usd,
            "daily_budget_usd": service.daily_budget_usd,
            "roles": pack.roles,
            "stages": pack.stages,
            "resolution_roles": pack.resolution_roles,
        }

    @app.get("/demo/scenarios")
    def demo_scenarios():
        return [{**scenario, "available": service.assessor is not None or not scenario["live"]} for scenario in catalog()]

    @app.get("/settings")
    def get_settings():
        return settings.describe()

    @app.put("/settings")
    def change_settings(request: SettingsRequest):
        return settings.change(request.model_dump(), request.actor_id, request.role)

    @app.post("/demo/scenarios/{scenario_id}", status_code=201)
    def start_demo_scenario(scenario_id: str):
        return start_scenario(scenario_id, offline_service, service)

    @app.get("/demo/models/{scenario_id}/{kind}")
    def demo_model(scenario_id: str, kind: str):
        headers = {"Content-Disposition": f'attachment; filename="{scenario_id}-{kind}.ifc"'}
        return Response(sample_model(scenario_id, kind), media_type="application/x-step", headers=headers)

    @app.get("/demo/documents/{scenario_id}/{document_type}")
    def demo_document(scenario_id: str, document_type: str, incomplete: bool = False):
        headers = {"Content-Disposition": f'attachment; filename="{document_type}.pdf"'}
        return Response(sample_document(scenario_id, document_type, incomplete), media_type="application/pdf", headers=headers)

    @app.get("/knowledge")
    def knowledge():
        return {
            "pack_version": pack.version,
            "labels": pack.labels,
            "rules": [
                {**rule.model_dump(include={"id", "title", "domain", "text", "reference", "requires_evidence"}), "source_url": pack.source(rule.source).url}
                for rule in pack.rules
            ],
            "gaps": [gap.model_dump(include={"id", "when", "description"}) for gap in pack.gaps],
            "documents": [{"type": name, **item.model_dump()} for name, item in pack.documents.items()],
            "sources": list(load_sources().values()),
            "cards": load_cards(),
            "index_available": retriever is not None,
        }

    @app.get("/knowledge/passages")
    def knowledge_passages(source: str | None = None, q: str | None = None, offset: int = 0, limit: int = 20):
        """Browse the index. Full source texts: internal use only."""
        if retriever is None:
            raise UnknownItem("no search index is available on this server")
        return retriever.browse(source, q, max(offset, 0), min(max(limit, 1), 100))

    @app.get("/knowledge/search")
    def knowledge_search(q: str, authority: str | None = None):
        """What retrieval would hand to a review for this text, with the limits in force."""
        if retriever is None:
            raise UnknownItem("no search index is available on this server")
        return {"terms": terms(q), "passages": retriever.search(q, authority)}

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
            {**event, "payload": {key: value for key, value in event["payload"].items() if key not in BULKY}}
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

    @app.post("/cases/{case_id}/documents")
    async def upload_document(case_id: str, request: Request, type: str, filename: str = "document.pdf"):
        if int(request.headers.get("content-length", 0)) > MAX_DOCUMENT_BYTES:
            raise InvalidRequest("the document is larger than 20 MB")
        content = await request.body()
        return await run_in_threadpool(service.register_document, case_id, type, filename, content)

    @app.get("/cases/{case_id}/documents/{evidence_id}/file")
    def document_file(case_id: str, evidence_id: str, version: int | None = None):
        content, filename = service.document_file(case_id, evidence_id, version)
        safe = "".join(char for char in filename if char.isalnum() or char in "._- ") or "document.pdf"
        headers = {"Content-Disposition": f'inline; filename="{safe}"', "X-Content-Type-Options": "nosniff"}
        return Response(content, media_type="application/pdf", headers=headers)

    @app.post("/cases/{case_id}/fact-decisions")
    def decide_fact(case_id: str, request: FactDecision):
        return service.decide_fact(case_id, request.model_dump())

    @app.post("/cases/{case_id}/document-decisions")
    def assess_document(case_id: str, request: DocumentDecision):
        return service.assess_document(case_id, request.model_dump())

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
    env = os.environ.get
    assessor = reader = None
    if env("REPERMIT_LLM_PROVIDER", "anthropic") != "none":
        # REPERMIT_LLM_MODEL is the older name for the review model.
        assessor = ClaudeAssessor(
            env("REPERMIT_AI_REVIEW_MODEL") or env("REPERMIT_LLM_MODEL") or MODEL,
            effort=env("REPERMIT_AI_REVIEW_EFFORT") or "high",
            max_tool_calls=int(env("REPERMIT_AI_BIM_TOOL_CALLS") or "6"),
        )
        if env("REPERMIT_AI_DOCUMENTS_MODEL"):
            reader = ClaudeAssessor(env("REPERMIT_AI_DOCUMENTS_MODEL"), effort=env("REPERMIT_AI_DOCUMENTS_EFFORT") or "medium")
    index = Path(env("REPERMIT_KNOWLEDGE_INDEX", "knowledge/index.sqlite"))
    return create_app(
        database_url,
        pack,
        assessor,
        Retriever(index) if index.exists() else None,
        case_budget_usd=float(env("REPERMIT_CASE_BUDGET_USD", "1.00")),
        daily_budget_usd=float(env("REPERMIT_DAILY_BUDGET_USD", "5.00")),
        document_reader=reader,
        assessor_factory=lambda model, effort: ClaudeAssessor(model, effort=effort),
        allowed_models=tuple(name.strip() for name in env("REPERMIT_AI_ALLOWED_MODELS", ",".join(DEFAULT_MODELS)).split(",") if name.strip()),
    )
