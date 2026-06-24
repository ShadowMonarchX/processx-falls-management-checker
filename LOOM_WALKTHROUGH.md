# Loom Walkthrough

## Demo Steps
1. Open the repository and show the input workbook.
2. Explain the policy parser and the structured rule set.
3. Run the validation flow.
4. Show provider selection and structured extraction logging.
5. Open the completed workbook and review resident output sheets.

## Talking Points
- The LLM extracts structured facts from nursing notes.
- The deterministic rule engine remains the final compliance authority.
- Output flags are policy-grounded and traceable.
- The workbook is populated in-place for the submission artifact.

## Architecture Explanation
- Policy DOCX is parsed into rule objects.
- Prompt builder injects policy and note context.
- LLM client selects Gemini, Claude, OpenAI, or local fallback.
- Structured output is validated before rule evaluation.
- Excel writer preserves the workbook template.

## AI Reasoning Explanation
- The model is used for structured extraction and semantic support.
- It does not make the final compliance decision.
- Rules decide pass/fail flags to keep the output explainable and deterministic.

## Policy Grounding Explanation
- Each flag maps back to a specific policy rule.
- Evidence and missing requirements are included in the explanation text.
- The system is designed to stay auditable for interview review.
