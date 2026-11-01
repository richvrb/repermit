# Design

## Context

The service is an API with an event log. See proposal.md for motivation. The event log already holds everything a flow view needs.

## Goals / Non-Goals

**Goals:**

- A viewer understands the process without knowing the API.
- The demo runs from the existing container, without a build step.

**Non-Goals:**

- Real login, multi-user use, or live updates between browsers.
- Uploading or reading real documents. Documents in the demo are simulated metadata.

## Decisions

**One static page without a framework.** `index.html` is served by FastAPI and uses plain JavaScript. All values are inserted as text nodes, because LLM output and case text are untrusted. Rejected: a React build, which adds tooling for one page.

**Replay by folding a prefix of the events.** `GET /cases/{id}?at=n` folds the first n events into the normal case view, so past steps need no separate logic.

**Questions come from two sources.** LLM `information_requests` are shown separately from rule deficiencies. Only deficiencies block the case; closing them needs evidence, so an AI question alone never holds or releases a case.

**Answers are evidence.** An answer is a versioned `statement` carrying a fact. Free text is a `note` with a description, which the LLM reads but rules ignore. The controls stay unchanged: facts proposed by the LLM still need a human answer.

**Reassessment is a user action.** Rules react to each addition immediately. A new LLM review needs a button, because it costs money and takes time.

**Fixed scenarios stay offline.** They run without the LLM, and only test cases marked live use it.

## Risks / Trade-offs

- [A live step takes up to a minute] → A visible busy state on the button.
- [The role selector is a simulation] → Stated in the interface; Compose stays on loopback.
- [Rejected requests leave no history, such as the PDF in the BIM case] → Shown as a message in the interface.
