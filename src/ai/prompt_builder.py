from src.core.models import PolicyRuleModel


class PromptBuilder:
    def build_policy_summary(self, rules: list[PolicyRuleModel]) -> str:
        return "\n".join(f"{rule.rule_id}: {rule.requirement}" for rule in rules)

