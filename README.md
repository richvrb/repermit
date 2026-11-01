# RePermit

Service for UC-01, *Process a Building-Permit Design Modification*. It assesses a proposed modification, determines the evidence needed and the permitted next step, and adapts when information changes.

RePermit does not issue permits, certify compliance or replace competent-authority decisions. Live cases use rules derived from public Dubai sources (see `docs/source-analysis.md`), and fixed test cases use a synthetic pack. Neither is official or complete Dubai Municipality/BPS logic. Actor roles are supplied by the client as a simulation, so do not expose the API publicly.

## Run with containers

```powershell
Copy-Item .env.example .env   # then set POSTGRES_PASSWORD
docker compose up --build -d
```

- Demo: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Readiness: http://127.0.0.1:8000/ready

## Demo

Open http://127.0.0.1:8000 to start a test case and follow it through the process. The timeline can be stepped through and replayed. Answer the open questions or add free text, and use the AI button to have Claude assess the case again. Test cases marked AI, your own requests and each new AI assessment make a paid Claude call.

From the command line, this creates synthetic cases for H0, E1-E6, T0-T5 and BIM delivery, and prints each with its stage and status. Each run adds new cases.

```powershell
docker compose exec api python -m repermit.demo
```

Inspect a case at `/cases/{case_id}` and its full trail at `/cases/{case_id}/history`.

## LLM review

Claude classifies and assesses every modification, and `change_type` may be left out so that the description alone is used. The review is advisory: rules and evidence decide domain status. A review can hold a case and withdraw its own earlier flag, but it cannot clear a domain, establish a fact or authorize an action. If no usable review is obtained, the case escalates; re-run it with `POST /cases/{case_id}/llm-review`.

## BIM models and review rounds

New permits and public-pack modifications need a real IFC design model. Upload it with `POST /cases/{case_id}/models?kind=proposed` (`kind=baseline` for the approved model), up to 50 MB. The app stores the parsed elements and the file hash, not the file. It compares the two models by `GlobalId` and derives `load_bearing`, `fire_compartment_boundary` and `facade_change` from the values stated on changed elements. Comparison uses declared properties, not geometry.

Each addition to a reviewed case triggers a new review. `POST /cases/{case_id}/responses` submits a whole round at once: fact answers, answers to AI questions, documents and a note. Open AI questions hold the case. After `max_review_rounds` reviews on a revision, remaining questions go to the authority.

Modification text, evidence metadata and model comparisons are sent to the Anthropic API, and each review has a cost. Set `ANTHROPIC_API_KEY` in `.env`, and `REPERMIT_LLM_PROVIDER=none` disables the LLM. This live scenario makes one paid call:

```powershell
docker compose exec api python -m repermit.demo --llm
```

## Develop

```powershell
python -m venv $env:USERPROFILE\.venvs\repermit
& $env:USERPROFILE\.venvs\repermit\Scripts\python -m pip install -e ".[dev]"
& $env:USERPROFILE\.venvs\repermit\Scripts\python -m pytest
```

Keep the virtual environment out of this synced folder. Specifications live in `openspec/`; use `/opsx:propose` in Claude Code, started from this folder, for new changes.

## Configuration

| Variable | Default |
| --- | --- |
| `REPERMIT_DATABASE_URL` | `sqlite:///repermit.db` (image: `/data/repermit.db`) |
| `REPERMIT_PACK_PATH` | bundled public-source pack |
| `ANTHROPIC_API_KEY` | none |
| `REPERMIT_LLM_PROVIDER` | `anthropic` (`none` disables the LLM) |
| `REPERMIT_LLM_MODEL` | `claude-opus-5-5` |
