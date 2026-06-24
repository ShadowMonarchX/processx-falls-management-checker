from src.core.models import PolicyRuleModel

class RuleMapper:
    def map(self, rules: list[PolicyRuleModel]) -> dict[str, PolicyRuleModel]:
        # A dictionary lookup keeps rule resolution O(1) when many notes reuse
        # the same policy identifiers across residents and days.
        return {rule.rule_id: rule for rule in rules}
