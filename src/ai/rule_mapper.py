from src.core.models import PolicyRuleModel

# This class is responsible for mapping a list of PolicyRuleModel instances to a dictionary where the keys are the rule IDs and the values are the corresponding PolicyRuleModel instances. This allows for efficient retrieval of rules based on their IDs.


class RuleMapper:
    def map(self, rules: list[PolicyRuleModel]) -> dict[str, PolicyRuleModel]:
        return {rule.rule_id: rule for rule in rules}
