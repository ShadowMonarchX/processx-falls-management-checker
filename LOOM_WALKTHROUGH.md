# Loom Walkthrough

Use this outline for a short demo of the project.

## 1. Introduce the Problem

- Explain that the checker validates resident progress notes against a falls management policy.
- Show that the source workbook contains one input sheet and one output sheet per resident.

## 2. Show the Main Workflow

- Point to `src/main.py`
- Explain that startup loads `.env`, validates the environment, and then runs the workbook pipeline
- Mention the `--health-check` mode for provider diagnostics

## 3. Explain the AI Layer

- Show `src/ai/llm_client.py`
- Describe the provider chain:
  - Local GGUF
  - Gemini
  - Claude
  - OpenAI
  - Ollama
  - Structured fallback
- Explain that AI is used for structured extraction, not final compliance decisions

## 4. Explain the Local Model Path

- Show `src/ai/model_registry.py`
- Show `src/ai/loader.py`
- Explain model caching, auto-download behavior, and device selection

## 5. Show the Deterministic Validator

- Show `src/services/compliance_engine.py`
- Explain that the rule engine turns extracted facts into explainable flags
- Emphasize that the final compliance decision is deterministic

## 6. Show Workbook Output

- Show `src/services/excel_writer.py`
- Explain that the checker writes to the existing template, not a regenerated workbook
- Point out that the completed workbook is saved both in `data/raw/Your_Output_File.xlsx` and `outputs/completed_output.xlsx`

## 7. Show the Logs

- Open `logs/processx.log`
- Highlight structured provider diagnostics
- Highlight the model download and fallback traces

## 8. Suggested Closing

- The app is explainable because every flag ties back to a policy rule
- The app is resilient because it uses provider fallback and health checks
- The app is practical because it preserves the workbook template and submission file

