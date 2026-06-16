from src.core.models import PolicyRuleModel


class RuleMapper:
    def map(self, rules: list[PolicyRuleModel]) -> dict[str, PolicyRuleModel]:
        return {rule.rule_id: rule for rule in rules}

