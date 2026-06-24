# Architecture

## Component Design
- `PolicyParserImpl` reads the policy DOCX and converts policy sections into `PolicyRuleModel` objects.
- `ComplianceEngine` evaluates each resident note against the day-specific rule set.
- `ValidationEngine` orchestrates workbook traversal and note validation.
- `ExcelWriter` writes the generated flags into the existing output sheets.
- `LLMClient` performs sequential provider fallback with retries and timeouts.

## Data Flow
1. Read policy DOCX.
2. Build structured rule objects.
3. Read workbook input sheets.
4. Create resident note models.
5. Validate notes against rules.
6. Write flags to the matching output sheet.

## Validation Flow
- Day 1 rules validate incident details, assessment, vital signs, and initial escalation documentation.
- Day 2 rules validate continuation notes and follow-up updates.
- Day 3 rules validate closure, escalation, and prevention review.
- Provider order is Gemini -> Claude -> OpenAI -> local Ollama.
- If a provider fails after retries or times out, the engine advances to the next provider.

## Rule Engine Flow
- Each rule carries a requirement, trigger phrases, and explanation template.
- The compliance engine matches the day number in the note to the relevant rule group.
- Missing or vague evidence produces a flag with a policy trace.
