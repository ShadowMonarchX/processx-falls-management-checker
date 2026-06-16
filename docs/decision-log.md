# Decision Log

1. Policy requirements were structured into typed rule objects with day number, requirement text, trigger phrases, and explanation templates so the validation layer could remain deterministic and explainable.
2. An AI-style suggestion to generate free-form summary flags such as "Documentation incomplete" was rejected because the workflow requires nurse-actionable, policy-traceable findings.
3. The ambiguous policy decision was how to treat vague wording like "advised to monitor" on Day 1 and "doing much better" on Day 3. It was resolved by flagging those notes as vague when the policy required a specific numeric or explicit clinical statement.
