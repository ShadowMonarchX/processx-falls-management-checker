# ProcessX Falls Management Compliance Checker

## Project Overview
This project reads a falls management policy and resident progress notes from Excel workbooks, extracts policy rules, validates each note against those rules, and writes policy-explainable compliance flags into the existing output worksheets.

## Business Problem
Care staff must document post-fall monitoring consistently and completely. The task is to detect missing, vague, incomplete, and non-compliant documentation so a nurse can see exactly what needs to be corrected.

## Solution Design
The checker uses:

- DOCX parsing to read the policy source of truth
- Structured policy rules to represent documentation requirements
- Excel parsing to locate resident input/output sheet pairs
- A hybrid AI extraction layer to support semantic interpretation of nursing notes
- A rule-based compliance engine to compare notes with policy requirements
- Workbook writing that preserves the template structure and formatting

## Architecture
The code is organized by clean architecture boundaries:

- `src/core` for shared contracts, constants, exceptions, and models
- `src/domain` for domain-specific model aliases
- `src/parsers` for document and workbook parsing
- `src/services` for validation and workbook output
- `src/ai` for prompt building, provider selection, and structured extraction
- `src/utils` for logging and filesystem helpers

## Folder Structure

```text
data/raw/
data/processed/
docs/
outputs/
src/
tests/
```

## Installation

```bash
pip install -r requirements.txt
```

Or with uv:

```bash
uv sync
```

## Execution

```bash
python src/main.py
```

Or:

```bash
uv run src/main.py
```

The generated workbook is written to `outputs/completed_output.xlsx`.

The official submission workbook is populated in-place at `data/raw/Your_Output_File.xlsx`.

## Validation Flow
1. Load the policy DOCX.
2. Extract structured requirements into rule objects.
3. Build a structured extraction prompt for each resident note.
4. Run the AI extraction layer with provider fallback.
5. Validate the extracted facts and note text against the deterministic rules.
6. Load the workbook and identify each resident input/output sheet pair.
7. Write policy-explainable flags into the output sheet.

## AI Architecture
- `PromptBuilder` injects the policy context and resident note into a JSON-only extraction prompt.
- `LLMClient` selects Gemini, Claude, OpenAI, or local LLM fallback based on available configuration.
- Structured AI output is validated before any rule evaluation occurs.
- The rule engine remains the final source of truth for compliance decisions.

## Provider Configuration
- Set `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` in `.env`.
- Provider priority is sequential: Gemini, then Claude, then OpenAI, then local fallback.
- If a provider times out or fails after retries, the client advances to the next provider.
- Local fallback uses `ollama` and can be paired with `qwen2.5:3b-instruct`, `qwen2.5:7b-instruct`, or `qwen3:14b`.
- Hosted provider support requires the corresponding SDKs installed through `requirements.txt` or `uv sync`.
- Local GGUF inference is cache-first and uses `MODEL_CACHE_DIR` (default `models/`).
- Set `LOCAL_GGUF_AUTO_DOWNLOAD=1` to allow automatic model download from Hugging Face on first use.
- Set `LOCAL_GGUF_ENABLED=0` to skip the GGUF provider entirely.
- Optional Hugging Face auth can be supplied via `HF_TOKEN` or `HUGGINGFACE_TOKEN`.
- `LLM_TIMEOUT_SECONDS` and `LLM_RETRY_COUNT` control provider timeout and retry behavior.

## Workbook Generation
- The output workbook preserves sheets, formatting, and the existing template layout.
- The completed artifact is written to `data/raw/Your_Output_File.xlsx`.
- A secondary copy may be generated for internal inspection, but the official workbook is the submission artifact.

## Assumptions
- The provided policy document is the source of truth.
- Existing workbook structure and formatting must be preserved.
- Output worksheets are already present and must be reused.
- One row in the input workbook represents one day of progress notes.

## Design Decisions
- The checker uses structured policy rules instead of free-form prompting during validation.
- AI is used for structured extraction and semantic support, not for final compliance verdicts.
- Each generated flag includes policy rule, trigger condition, evidence, missing requirement, and recommendation.
- Workbook updates append into the blank output table rather than recreating sheets.

## Limitations
- The implementation is focused on the supplied policy and workbook patterns.
- The model layer depends on provider credentials or a local LLM runtime for full AI behavior.

## Future Improvements
- Expand the rule mapper to support additional policy documents.
- Add more granular field-level extraction for richer explanations.
- Extend the workbook writer to preserve row heights and styling when appending large volumes of flags.
