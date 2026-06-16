from pathlib import Path

from src.parsers.policy_parser import PolicyParserImpl


def test_policy_parser_extracts_structured_rules():
    rules = PolicyParserImpl(Path("data/raw/Falls_Management_Policy_ProcessX.docx")).parse()
    assert [rule.day for rule in rules] == [1, 1, 1, 1, 2, 3]
    assert any(rule.rule_id == "D1_ACTIONS" for rule in rules)
    assert any(rule.rule_id == "D3_CLOSE" for rule in rules)
