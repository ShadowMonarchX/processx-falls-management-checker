# Architecture

The solution uses a clean, policy-driven pipeline:

1. `src/parsers/policy_parser.py` reads the policy document and converts the documentation requirements into structured rule objects.
2. `src/services/compliance_engine.py` applies day-specific validation logic to each resident note.
3. `src/services/validation_engine.py` loads the workbook, processes each resident day by day, and coordinates output writing.
4. `src/services/excel_writer.py` preserves workbook structure while appending generated flags into the existing output sheets.
5. `src/main.py` wires the components together and writes the completed workbook to `outputs/completed_output.xlsx`.

The implementation prioritizes explainability over heuristic breadth. Every generated flag is designed to map back to a policy rule, a trigger condition, and a user-facing recommendation.

