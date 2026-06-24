# ProcessX — AIML Fresher Interview Task

Welcome. This repository contains the completed checker, the policy source document, the sample workbook, and the submission workbook.

## What’s Included

| File | Purpose |
|---|---|
| `ProcessX_AIML_Task_Brief.docx` | Full task brief |
| `Falls_Management_Policy_ProcessX.docx` | Policy source of truth |
| `Sample_Input_Output.xlsx` | Sample workbook used for validation |
| `Your_Output_File.xlsx` | Official submission workbook updated by the checker |

## Project Summary

This project reads nursing progress notes, extracts structured facts with AI support, validates each note against the falls policy, and writes clear compliance flags into the workbook output sheets.

Current behavior:

- Local GGUF is the preferred provider
- Gemini, Claude, OpenAI, and Ollama are fallback providers
- The deterministic rule engine remains the final compliance authority
- The official workbook is populated in place at `data/raw/Your_Output_File.xlsx`

## How to Use the Files

### 1. Read the brief and the policy

- `ProcessX_AIML_Task_Brief.docx` explains the task requirements
- `Falls_Management_Policy_ProcessX.docx` explains the compliance criteria
- Section 5 of the policy is the most important section

### 2. Study the sample workbook

`Sample_Input_Output.xlsx` contains:

| Sheet | Meaning |
|---|---|
| `John Doe - Input` | Clean notes, should produce no flags |
| `John Doe - Output` | Expected empty output |
| `Peter Parker - Input` | Notes with missing and vague entries |
| `Peter Parker - Output` | Expected flagged output |

Use the sample workbook to understand the output style and the level of detail expected in the flags.

### 3. Run the checker on the real workbook

`Your_Output_File.xlsx` contains:

| Resident | Notes |
|---|---|
| Alice Nguyen | 3 days |
| Robert Singh | 3 days |
| Edna Kowalski | 3 days |
| Thomas Brennan | 3 days |

The checker writes output into the matching `Your Output` sheets and also creates `outputs/completed_output.xlsx`.

## What to Submit

1. Your repository with setup instructions in `README.md`
2. The completed `Your_Output_File.xlsx`
3. A decision log
4. A Loom walkthrough

## What the Reviewer Will Look For

- Clear policy understanding
- Thoughtful AI usage
- Specific, explainable flags
- Deterministic final compliance decisions

