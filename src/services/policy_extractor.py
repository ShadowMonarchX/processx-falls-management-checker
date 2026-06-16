from pathlib import Path

from src.core.models import PolicyRuleModel
from src.parsers.policy_parser import PolicyParserImpl


class PolicyExtractor:
    def __init__(self, policy_path: Path) -> None:
        self._parser = PolicyParserImpl(policy_path)

    def extract(self) -> list[PolicyRuleModel]:
        return self._parser.parse()

