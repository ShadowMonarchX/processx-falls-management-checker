# Architecture

## Component Design
- `PolicyParserImpl` reads the policy DOCX and converts policy sections into `PolicyRuleModel` objects.
- `ComplianceEngine` evaluates each resident note against the day-specific rule set.
- `ValidationEngine` orchestrates workbook traversal and note validation.
- `ExcelWriter` writes the generated flags into the existing output sheets.
- `LLMClient` performs sequential provider fallback with retries, timeouts, provider health caching, and structured logging.
- `src/ai/device.py` detects the runtime device and GPU capability.
- `src/ai/model_registry.py` stores the GGUF model registry.
- `src/ai/loader.py` resolves, downloads, caches, and loads the local GGUF model.
- `src/ai/health.py` exposes provider readiness and model diagnostics.

## Data Flow
1. Read policy DOCX.
2. Build structured rule objects.
3. Read workbook input sheets.
4. Create resident note models.
5. Validate notes against rules.
6. Write flags to the matching output sheet.
7. Save the finished workbook to the official submission file and the secondary output copy.

## Validation Flow
- Day 1 rules validate incident details, assessment, vital signs, and escalation documentation.
- Day 2 rules validate continuation notes and follow-up updates.
- Day 3 rules validate closure, escalation, and prevention review.
- Provider order is Local GGUF -> Gemini -> Claude -> OpenAI -> Ollama -> structured fallback.
- Provider failures are logged with structured error details and traceback.
- Providers that fail are marked unhealthy for the remainder of the process, reducing repeated retries on later notes.

## Startup Flow
- `.env` is loaded before the app imports the rest of the runtime modules.
- Startup validation checks workbook paths, cache paths, and provider configuration.
- `--health-check` prints a provider readiness summary without running the workbook pipeline.

## Rule Engine Flow
- Each rule carries a requirement, trigger phrases, and explanation template.
- The compliance engine matches the day number in the note to the relevant rule group.
- Missing or vague evidence produces a flag with a policy trace.

## AI Behavior
- Local GGUF is the preferred provider and can auto-download its model when the cache is empty.
- Gemini, Claude, and OpenAI are hosted fallbacks when their API keys are configured.
- Ollama is the final runtime fallback before the structured fallback payload.
- Structured fallback is only used after every provider has failed.
