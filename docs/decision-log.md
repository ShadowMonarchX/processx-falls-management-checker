# Decision Log

1. Policy requirements were structured into typed rule objects with day number, requirement text, trigger phrases, and explanation templates so the validation layer could remain deterministic and explainable.
2. Free-form summary flags such as "Documentation incomplete" were rejected because the workbook output must be nurse-actionable and policy-traceable.
3. The ambiguous policy decision was how to treat vague wording like "advised to monitor" on Day 1 and "doing much better" on Day 3. It was resolved by flagging those notes as vague when the policy required a specific numeric or explicit clinical statement.
4. Policy context is injected into the AI extraction prompt as structured requirements so the model can support fact extraction without owning compliance decisions.
5. A hybrid AI plus rules architecture was chosen so the model can improve semantic interpretation while the deterministic engine remains the final source of truth.
6. Prompt version `extraction_v1` is used for structured note extraction, while compliance verdicts remain rule-based to avoid hallucinated pass/fail outcomes.
7. Sequential provider fallback is implemented at runtime as Local GGUF, Gemini, Claude, OpenAI, Ollama, then structured fallback, with provider health tracking to avoid repeated retries on providers that already failed.
8. Provider failures are logged with structured error details and tracebacks so the runtime path can be audited from logs.
9. Startup now emits structured diagnostics for environment, cache, and provider readiness so a reviewer can quickly see whether the app is configured for live AI or fallback-only behavior.
10. The official workbook is written in place and also saved as a secondary output copy to keep the submission artifact easy to locate.
