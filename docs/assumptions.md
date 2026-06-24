# Assumptions

## Policy Assumptions
- Section 5 of the falls policy governs the validation criteria for Day 1, Day 2, and Day 3 notes.
- The policy text in the supplied DOCX is complete enough to derive the required rule set.
- Policy requirements are stable for the supplied task workbook and do not change at runtime.

## Workbook Assumptions
- Each resident has one input sheet and one output sheet.
- Output sheets already contain the correct formatting and header rows.
- Rows starting at row 4 represent the editable output area.
- The submission workbook must be updated in place at `data/raw/Your_Output_File.xlsx`.
- A secondary completed copy is also written to `outputs/completed_output.xlsx`.

## Validation Assumptions
- Notes are interpreted as one note per day.
- The checker reports only policy-derived issues.
- A phrase such as "will update" or "advised to monitor" is treated as insufficient when the policy requires a specific confirmed action.
- AI extraction supports the validator, but the rule engine remains the final decision maker.
