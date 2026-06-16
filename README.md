# ProcessX Falls Management Documentation Compliance Checker

## Project Overview

This project implements a policy-driven compliance checker for post-fall nursing documentation. It reads resident progress notes, extracts validation rules from the Falls Management Policy, and writes specific compliance flags back into the provided workbook structure.

## Business Problem

After a resident fall, care staff must document immediate actions and follow-up monitoring across three consecutive days. Missing, incomplete, or vague documentation creates clinical risk and makes it hard to prove policy compliance.

## Solution Architecture

The solution is built with a layered architecture:

- `parsers` read DOCX and XLSX sources
- `services` apply policy extraction, note analysis, validation, and workbook writing
- `domain` and `core` define the rule and flag models
- `ai` contains future extension points for LLM-assisted rule mapping

## Folder Structure

- `data/raw` source brief, policy, and workbooks
- `data/processed` reserved for intermediate artifacts
- `outputs` completed workbook output
- `docs` architecture, assumptions, and decision log
- `src` application code
- `tests` unit and integration tests

## Installation

Using pip:

```bash
pip install -r requirements.txt
```

## Setup

Copy `.env.example` to `.env` if you want to customize input or output paths.

## Execution

Run the checker:

```bash
python src/main.py
```

The completed workbook is written to `outputs/completed_output.xlsx`.

## Validation Process

1. Parse the policy document into structured rules.
2. Read each resident's input worksheet.
3. Validate Day 1, Day 2, and Day 3 notes against the policy.
4. Generate specific, explainable flags.
5. Append the flags into the corresponding output worksheet.
6. Save the completed workbook.

## Design Decisions

- The policy is converted into explicit rule objects instead of being re-sent to an LLM on every note.
- Flags are day-specific and policy-linked to make interview explanation straightforward.
- The workbook writer preserves the existing structure and only appends rows.

## Assumptions

- The policy document is authoritative.
- The sample workbook represents the expected style of valid flags.
- Day labels follow a three-day sequence.

## Limitations

- The current engine is deterministic and does not use a live LLM.
- The checker focuses on the provided falls-management task and does not generalize to unrelated documentation domains without new rules.

## Future Improvements

- Expand the policy parser to infer more rules automatically from policy prose.
- Add richer natural-language explanation generation.
- Preserve cell styling when appending new rows.
- Add workbook-level verification for downstream interview review.

