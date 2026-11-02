# Proposal

## Why

The source research found that the ruleset cites a replaced article, applies authority-specific rules everywhere, and misses the legal basis for the second owner.

## What Changes

- Cite Local Order 3/1999 art. 4 as replaced by Resolution 65/2022, and treat simple maintenance separately.
- Limit DDA and Dubai Municipality rules to their authority, and add Dubai Municipality equivalents.
- Base the Civil Defence NOC on Law 4/2025 for every authority.
- Add planning-use, ownership and fire-value gaps and rules.
- Publish this as pack version `dubai-public-2026.2`, and keep the earlier version for existing cases.

## Capabilities

### New Capabilities

- `public-source-rules`: Corrections to the public ruleset.

### Modified Capabilities

None. This change builds on changes that have not been archived yet.

## Impact

- Changes to `dubai_public.yaml`, `knowledge.py`, `api.py` and `docs/source-analysis.md`.
- More cases escalate, on purpose: fire separations and moved unit boundaries now go to a reviewer.
