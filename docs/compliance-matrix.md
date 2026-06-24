# ProcessX Compliance Matrix

| Requirement | Status | Evidence |
| --- | --- | --- |
| Read policy DOCX | PASS | `src/parsers/policy_parser.py` loads `Falls_Management_Policy_ProcessX.docx` |
| Validate notes against policy | PASS | `src/services/compliance_engine.py` |
| Use AI in runtime | PARTIAL | `src/ai/llm_client.py`, `src/services/validation_engine.py` |
| Structured AI output | PASS | `src/core/models.py::StructuredExtractionModel` |
| Provider fallback | PASS | `src/ai/llm_client.py::select_provider` and provider call fallbacks |
| Preserve deterministic validation | PASS | `src/services/compliance_engine.py` remains final validator |
| Populate official workbook | PASS | `data/raw/Your_Output_File.xlsx` |
| Preserve workbook formatting | PASS | `src/services/excel_writer.py` writes into existing template |
| Decision log | PASS | `docs/decision-log.md` |
| Loom walkthrough guide | PASS | `LOOM_WALKTHROUGH.md` |
| README setup instructions | PASS | `README.md` |
| Tests for AI integration | PASS | `tests/test_ai_integration.py` |
