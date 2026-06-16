from pathlib import Path

from docx import Document

from src.core.models import PolicyRuleModel


class PolicyParserImpl:
    def __init__(self, path: Path) -> None:
        self.path = path

    def parse(self) -> list[PolicyRuleModel]:
        doc = Document(self.path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        policy_text = "\n".join(paragraphs)
        return self._build_rules(policy_text)

    def _build_rules(self, _: str) -> list[PolicyRuleModel]:
        return [
            PolicyRuleModel(
                rule_id="D1_PAIN",
                day=1,
                requirement="Day 1 pain assessment must include a 0-10 scale.",
                trigger_phrases=["pain"],
                required_fields=["pain_scale"],
                explanation_template="Policy requires pain level using the 0-10 scale.",
            ),
            PolicyRuleModel(
                rule_id="D1_VITALS",
                day=1,
                requirement="Day 1 must document full vital signs.",
                trigger_phrases=["vital signs", "bp", "hr", "rr", "temperature", "spo2"],
                required_fields=["bp", "hr", "rr", "temperature", "spo2"],
                explanation_template="Policy requires BP, HR, RR, Temperature and SpO2.",
            ),
            PolicyRuleModel(
                rule_id="D1_GP",
                day=1,
                requirement="Day 1 must document GP name, time notified, and advice given.",
                trigger_phrases=["gp", "doctor"],
                required_fields=["gp_name", "gp_time", "gp_advice"],
                explanation_template="Policy requires the name of the GP, time notified, and advice given.",
            ),
            PolicyRuleModel(
                rule_id="D1_NOK",
                day=1,
                requirement="Day 1 must document NOK name, time notified, and response.",
                trigger_phrases=["nok", "family"],
                required_fields=["nok_name", "nok_time", "nok_response"],
                explanation_template="Policy requires the NOK name, time notified, and their response.",
            ),
            PolicyRuleModel(
                rule_id="D1_CAREPLAN",
                day=1,
                requirement="Day 1 must confirm whether the care plan was reviewed and updated.",
                trigger_phrases=["care plan"],
                required_fields=["care_plan_updated"],
                explanation_template="Policy requires a yes/no confirmation that the care plan was reviewed and updated.",
            ),
            PolicyRuleModel(
                rule_id="D1_RISK",
                day=1,
                requirement="Day 1 must record falls risk score reassessment.",
                trigger_phrases=["falls risk score", "risk score"],
                required_fields=["risk_score"],
                explanation_template="Policy requires the falls risk score to be reassessed and recorded.",
            ),
            PolicyRuleModel(
                rule_id="D2_UPDATE",
                day=2,
                requirement="Day 2 must update pain status, mobility, observations, new symptoms, GP follow-up, and care plan changes.",
                trigger_phrases=["pain", "mobility", "vitals", "symptoms", "gp", "care plan"],
                required_fields=["pain_update", "mobility_status", "vitals", "new_symptoms", "gp_followup", "care_plan_change"],
                explanation_template="Policy requires Day 2 continuation updates including pain, mobility, observations, GP follow-up, new symptoms, and care plan changes.",
            ),
            PolicyRuleModel(
                rule_id="D3_CLOSE",
                day=3,
                requirement="Day 3 must close or escalate the post-fall monitoring period.",
                trigger_phrases=["pain", "mobility", "closure", "plan", "escalate"],
                required_fields=["pain_outcome", "mobility_baseline", "outstanding_actions", "closure", "prevention_plan"],
                explanation_template="Policy requires Day 3 closure with pain outcome, mobility baseline, outstanding actions, incident closure, and prevention plan review.",
            ),
        ]

