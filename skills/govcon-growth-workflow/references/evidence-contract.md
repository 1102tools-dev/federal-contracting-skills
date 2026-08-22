# Research evidence contract

The internal JSON record uses schema version `1.1` and these top-level fields:

```json
{
  "schema_version": "1.1",
  "skill": "market-research-workflow",
  "workflow_mode": "complete_report",
  "question": "What market evidence informs this acquisition?",
  "scope": {"as_of_date": "2026-08-21", "agency": null, "naics": [], "psc": [], "period": null},
  "document_register": [],
  "user_context": [],
  "assumptions": [],
  "web_research": {
    "mode": "no_public_web",
    "approved": true,
    "approved_at": "2026-08-21T18:00:00Z",
    "disclosure_acknowledged": true,
    "planned_providers": [],
    "providers_used": [],
    "fallback_events": []
  },
  "queries": [],
  "evidence": [],
  "findings": [],
  "inferences": [],
  "user_decisions": [],
  "conflicts": [],
  "unresolved_questions": [],
  "outputs": [],
  "validation": {}
}
```

Every evidence item has a stable ID such as `E001`, source class, title, locator or operation, retrieval time, as-of date when known, concise fact, and limitations. Source classes are `document`, `federal_mcp`, `official_web`, `other_web`, `user_statement`, and `calculation`.

Every finding has a stable ID such as `F001`, text, and one or more supporting evidence IDs. Inferences have their own IDs, cite evidence IDs, and state the reasoning and uncertainty. Queries record provider, semantic operation, sanitized parameters, retrieval time, count or coverage, and limitations. The `web_research` object records explicit approval, planned and used providers, and any approved fallback. Never store credentials or sensitive source text.

Use `scripts/validate_research_record.py` before generating an artifact. The validator rejects duplicate IDs, unknown evidence references, missing required fields, unapproved enumerations, secrets, and unsafe query keys.
