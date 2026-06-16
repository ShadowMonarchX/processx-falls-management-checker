from pathlib import Path

from src.parsers.policy_parser import PolicyParserImpl


def test_policy_parser_extracts_rules():
    rules = PolicyParserImpl(Path("data/raw/Falls_Management_Policy_ProcessX.docx")).parse()
    assert len(rules) >= 6
    assert any(rule.rule_id == "D1_PAIN" for rule in rules)
    assert any(rule.rule_id == "D3_CLOSE" for rule in rules)

