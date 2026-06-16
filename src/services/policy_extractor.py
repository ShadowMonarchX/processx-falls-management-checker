from pathlib import Path

from src.core.models import PolicyRuleModel
from src.parsers.policy_parser import PolicyParserImpl


# PolicyExtractor is a simple service that uses the PolicyParserImpl to extract the policy rules from the .docx file and return them as structured objects.
# It is used to extract the policy rules from the .docx file, which are then processed by the LLM to validate the resident documentation against the policy requirements.
class PolicyExtractor:
    def __init__(self, policy_path: Path) -> None:
        self._parser = PolicyParserImpl(policy_path)

    def extract(self) -> list[PolicyRuleModel]:
        return self._parser.parse()
