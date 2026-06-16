# Decision Log

1. Policy structured for AI consumption

The policy was converted into day-scoped validation rules with explicit required fields, trigger phrases, and explanation templates. This keeps the validation engine deterministic while still preserving traceability back to the policy section that inspired each rule.

2. AI-generated suggestion rejected

An early suggestion was to produce a single generic flag such as "documentation incomplete" when a field was missing. That was rejected because the task requires nurse-friendly, highly specific flags that identify exactly what must be corrected.

3. Ambiguity resolved by human decision

The policy says Day 2 should document whether the resident can full weight-bear without pain, but real notes often phrase this more loosely. The implementation resolves that ambiguity by only accepting explicit weight-bearing language or a clear functional statement; vague statements are flagged for clarification.

