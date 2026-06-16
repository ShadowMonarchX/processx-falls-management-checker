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
- A rule-based compliance engine to compare notes with policy requirements
- Workbook writing that preserves the template structure and formatting

## Architecture
The code is organized by clean architecture boundaries:

- `src/core` for shared contracts, constants, exceptions, and models
- `src/domain` for domain-specific model aliases
- `src/parsers` for document and workbook parsing
- `src/services` for validation and workbook output
- `src/ai` for prompt and rule mapping utilities
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

## Validation Flow
1. Load the policy DOCX.
2. Extract structured requirements into rule objects.
3. Load the workbook and identify each resident input/output sheet pair.
4. Parse each day’s progress note into a resident note model.
5. Apply the policy rules for that day.
6. Write policy-explainable flags into the output sheet.

## Assumptions
- The provided policy document is the source of truth.
- Existing workbook structure and formatting must be preserved.
- Output worksheets are already present and must be reused.
- One row in the input workbook represents one day of progress notes.

## Design Decisions
- The checker uses structured policy rules instead of free-form prompting during validation.
- Each generated flag includes policy rule, trigger condition, evidence, missing requirement, and recommendation.
- Workbook updates append into the blank output table rather than recreating sheets.

## Limitations
- The implementation is focused on the supplied policy and workbook patterns.
- It is rule-based rather than a live LLM integration at validation time.

## Future Improvements
- Expand the rule mapper to support additional policy documents.
- Add more granular field-level extraction for richer explanations.
- Extend the workbook writer to preserve row heights and styling when appending large volumes of flags.
