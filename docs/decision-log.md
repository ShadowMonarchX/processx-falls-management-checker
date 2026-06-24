# Decision Log

1. Policy requirements were structured into typed rule objects with day number, requirement text, trigger phrases, and explanation templates so the validation layer could remain deterministic and explainable.
2. An AI-style suggestion to generate free-form summary flags such as "Documentation incomplete" was rejected because the workflow requires nurse-actionable, policy-traceable findings.
3. The ambiguous policy decision was how to treat vague wording like "advised to monitor" on Day 1 and "doing much better" on Day 3. It was resolved by flagging those notes as vague when the policy required a specific numeric or explicit clinical statement.
4. Policy context is now injected into the AI extraction prompt as structured requirements so the model can support fact extraction without owning compliance decisions.
5. A hybrid AI plus rules architecture was chosen so the model can improve semantic interpretation while the deterministic engine remains the final source of truth.
6. Prompt version `extraction_v1` was chosen for structured note extraction, while a manual decision was made to keep compliance verdicts rule-based to avoid hallucinated pass/fail outcomes.
