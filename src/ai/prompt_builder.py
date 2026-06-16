from src.core.models import PolicyRuleModel

# This class is responsible for building prompts based on a list of PolicyRuleModel instances. It provides a method to create a summary of the policy rules, which can be used in various contexts such as generating reports or feeding into an AI model for further processing.


class PromptBuilder:
    def build_policy_summary(self, rules: list[PolicyRuleModel]) -> str:
        return "\n".join(f"{rule.rule_id}: {rule.requirement}" for rule in rules)
