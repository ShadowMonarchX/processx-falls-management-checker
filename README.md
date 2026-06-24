# ProcessX Falls Management Compliance Checker

ProcessX is a Python checker that reads a falls management policy, extracts resident note facts with AI support, validates the notes against policy rules, and writes explainable compliance flags into the workbook template.

## What This Project Does

- Parses the policy DOCX into structured rules
- Reads resident notes from the input workbook
- Uses AI extraction to turn notes into structured facts
- Applies deterministic compliance rules
- Writes output flags into the resident output sheets
- Saves the completed workbook both in the official submission file and in a secondary output copy

## Project Layout

```text
data/raw/              Source workbook, policy DOCX, submission workbook
docs/                  Architecture notes, assumptions, decisions, compliance matrix
prompts/               Prompt templates used for AI extraction and compliance support
src/                   Application code
tests/                 Unit and integration tests
outputs/               Generated completed workbook copy
logs/                  Runtime logs
```

## Core Workflow

1. Load environment variables from `.env`
2. Validate startup paths and provider configuration
3. Parse the policy document into rule objects
4. Traverse each resident input sheet
5. Build an extraction prompt for each note
6. Run the provider chain
7. Validate the structured extraction against the rule engine
8. Write compliance flags to the output sheet
9. Save the workbook to:
   - `data/raw/Your_Output_File.xlsx`
   - `outputs/completed_output.xlsx`

## Provider Order

The runtime provider chain is:

1. Local GGUF
2. Gemini
3. Claude
4. OpenAI
5. Ollama
6. Structured fallback

Local GGUF is the preferred provider. If the model file is missing, the app attempts to download it from Hugging Face when auto-download is enabled.

## Local Model

Primary model:

- Repo: `bartowski/Llama-3.2-1B-Instruct-GGUF`
- File: `Llama-3.2-1B-Instruct-Q4_K_M.gguf`
- Cache directory: `models/llama-3.2-1b/`

Device selection:

- CUDA -> `n_gpu_layers=-1`
- MPS -> `n_gpu_layers=-1`
- CPU -> `n_gpu_layers=0`

## Environment Setup

Create a `.env` file from `.env.example`.

Required and defaulted values:

```env
INPUT_WORKBOOK=data/raw/Your_Output_File.xlsx
OUTPUT_WORKBOOK=outputs/completed_output.xlsx
MODEL_CACHE_DIR=models
LOG_LEVEL=INFO
LLM_TIMEOUT_SECONDS=120
LLM_RETRY_COUNT=3
LOCAL_GGUF_ENABLED=1
LOCAL_GGUF_AUTO_DOWNLOAD=true
HF_TOKEN=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-pro
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b-instruct
```

Optional:

- `HF_TOKEN` for private Hugging Face access
- `LOCAL_GGUF_AUTO_DOWNLOAD=false` if you want cache-only behavior
- `LOCAL_GGUF_ENABLED=0` to skip the local GGUF provider

## Installation

Using pip:

```bash
pip install -r requirements.txt
```

Using uv:

```bash
uv sync
```

## Run

Run the checker:

```bash
python src/main.py
```

Or with uv:

```bash
uv run src/main.py
```

Health check only:

```bash
python src/main.py --health-check
```

## Expected Outputs

- Official workbook: `data/raw/Your_Output_File.xlsx`
- Secondary generated copy: `outputs/completed_output.xlsx`
- Runtime logs: `logs/processx.log`

## Logging

The app now emits structured logs for:

- Startup validation
- Provider diagnostics
- Provider request start/completion/failure
- Local GGUF model status
- Model download events
- Workbook write/save events

## Tests

Run the test suite:

```bash
pytest -q
```

Or:

```bash
uv run pytest -q
```

## Notes for Reviewers

- The deterministic compliance engine remains the final source of truth.
- AI is used for structured extraction and semantic support, not for final pass/fail decisions.
- The repository includes a health-check mode to quickly inspect provider readiness.
- Tests are configured to avoid accidental model downloads.

