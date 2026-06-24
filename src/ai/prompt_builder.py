from src.core.models import PolicyRuleModel


class PromptBuilder:
    def build_policy_summary(self, rules: list[PolicyRuleModel]) -> str:
        # Collapse policy rules into a compact reference block so the model can
        # reason over the policy without paying for repeated verbose phrasing.
        return "\n".join(f"{rule.rule_id}: {rule.requirement}" for rule in rules)

    def build_extraction_prompt(self, resident_name: str, day: str, note_text: str, rules: list[PolicyRuleModel]) -> str:
        policy_summary = self.build_policy_summary(rules)
        # The prompt is deliberately explicit about the output schema because
        # downstream extraction and validation assume predictable JSON keys.
        return (
            "You are extracting structured facts from a nursing note.\n"
            "Do not invent facts. Do not make compliance decisions.\n"
            "Return JSON only with keys: resident_name, day, observations, evidence, missing_items, confidence.\n"
            f"Resident: {resident_name}\n"
            f"Day: {day}\n"
            f"Policy requirements:\n{policy_summary}\n"
            f"Note:\n{note_text}"
        )
