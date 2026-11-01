# Tasks

## 1. Knowledge

- [x] 1.1 Extend the pack model with provenance, list conditions, fact questions and labels; verify with `tests/test_public_pack.py`
- [x] 1.2 Write `packs/dubai_public.yaml` and `docs/source-analysis.md`; verify the pack loads and every rule has a reference

## 2. Cases

- [x] 2.1 Record the pack per case and resolve it in the service; verify fixed and earlier cases stay synthetic in `tests/test_public_pack.py`
- [x] 2.2 Ask one unknown fact per rule with pack questions; verify with `tests/test_public_pack.py`

## 3. LLM and interface

- [x] 3.1 Give the LLM rule content and show it in the interface; verify with `tests/test_llm.py` and in a browser

## 4. Integration

- [x] 4.1 Rebuild the Compose stack and run a live case on the public pack; verify classification, questions and a recorded review
