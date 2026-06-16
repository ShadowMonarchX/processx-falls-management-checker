from pathlib import Path

from docx import Document

from src.core.exceptions import ParseError
from src.core.models import PolicyRuleModel

# PolicyParserImpl is a simple parser for the falls management policy .docx file that extracts the policy rules and converts them into structured objects.
# It is used to extract the policy rules from the .docx file, which are then processed by the LLM to validate the resident documentation against the policy requirements.
# The parser looks for specific trigger phrases and required fields in the policy text to build a list of PolicyRuleModel objects that can be used for validation.
# The parser also includes error handling to ensure that the policy text contains the expected sections and phrases, and raises a ParseError if the policy text is not in the expected format. This helps ensure that the validation logic has a consistent and reliable set of rules to work with.


class PolicyParserImpl:
    def __init__(self, path: Path) -> None:
        self.path = path

    def parse(self) -> list[PolicyRuleModel]:
        if not self.path.exists():
            raise ParseError(f"Policy file not found: {self.path}")
        doc = Document(self.path)
        paragraphs = [
            paragraph.text.strip()
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        ]
        policy_text = "\n".join(paragraphs)
        return self._build_rules(policy_text)

    def _build_rules(self, policy_text: str) -> list[PolicyRuleModel]:
        if (
            "Day 1" not in policy_text
            or "Day 2" not in policy_text
            or "Day 3" not in policy_text
        ):
            raise ParseError("Policy text is missing expected day sections")
        # The policy is converted into day-scoped rule objects so validation can stay deterministic
        # and every flag can be traced back to one policy requirement instead of a free-form prompt.
        return [
            PolicyRuleModel(
                rule_id="D1_FALL_DETAILS",
                day=1,
                requirement="Day 1 must document the date and time of fall, location, and whether the fall was witnessed.",
                trigger_phrases=[
                    "date and time of fall",
                    "location of fall",
                    "whether the fall was witnessed",
                ],
                required_fields=["date_time_of_fall", "location", "witnessed"],
                explanation_template="Policy requires the incident details to be documented on Day 1.",
                missing_phrases=["time of fall", "witnessed", "room", "area"],
            ),
            PolicyRuleModel(
                rule_id="D1_ASSESSMENT",
                day=1,
                requirement="Day 1 must document pain level, consciousness, visible injury, and ability to move all limbs.",
                trigger_phrases=[
                    "pain level",
                    "consciousness",
                    "visible injury",
                    "ability to move all limbs",
                ],
                required_fields=[
                    "pain_scale",
                    "consciousness",
                    "injury",
                    "limb_movement",
                ],
                explanation_template="Policy requires a documented initial condition assessment.",
                missing_phrases=[
                    "0-10",
                    "alert",
                    "orientated",
                    "able to move",
                    "visible",
                ],
                vague_phrases=["pain", "alert", "mobile"],
            ),
            PolicyRuleModel(
                rule_id="D1_VITALS",
                day=1,
                requirement="Day 1 must document vital signs BP, HR, RR, Temperature, and SpO2.",
                trigger_phrases=[
                    "vital signs",
                    "bp",
                    "hr",
                    "rr",
                    "temperature",
                    "spo2",
                ],
                required_fields=["bp", "hr", "rr", "temperature", "spo2"],
                explanation_template="Policy requires a full set of observations on Day 1.",
                missing_phrases=["bp", "hr", "rr", "temp", "spo2"],
            ),
            PolicyRuleModel(
                rule_id="D1_ACTIONS",
                day=1,
                requirement="Day 1 must document immediate actions, GP notification details, NOK notification details, conditional actions, risk factors, care plan review, and falls risk score reassessment.",
                trigger_phrases=[
                    "immediate actions",
                    "gp",
                    "nok",
                    "conditional actions",
                    "risk factors",
                    "care plan",
                    "falls risk score",
                ],
                required_fields=[
                    "immediate_actions",
                    "gp_details",
                    "nok_details",
                    "conditional_actions",
                    "risk_factors",
                    "care_plan_update",
                    "risk_score",
                ],
                explanation_template="Policy requires the full follow-up documentation for Day 1.",
                vague_phrases=["monitor", "will update", "family has been informed"],
            ),
            PolicyRuleModel(
                rule_id="D2_UPDATE",
                day=2,
                requirement="Day 2 must document pain status, mobility status, new symptoms, observations, GP follow-up, and care plan changes.",
                trigger_phrases=[
                    "pain status",
                    "mobility status",
                    "new symptoms",
                    "observations",
                    "gp follow-up",
                    "care plan",
                ],
                required_fields=[
                    "pain_status",
                    "mobility_status",
                    "symptoms",
                    "vitals",
                    "gp_followup",
                    "care_plan_change",
                ],
                explanation_template="Policy requires continuation documentation on Day 2.",
                missing_phrases=[
                    "improved",
                    "worsened",
                    "resolved",
                    "weight-bear",
                    "symptoms",
                    "bp",
                    "hr",
                    "rr",
                    "temp",
                    "spo2",
                ],
                vague_phrases=[
                    "seems okay",
                    "doing much better",
                    "moving around",
                    "mobilising",
                ],
            ),
            PolicyRuleModel(
                rule_id="D3_CLOSE",
                day=3,
                requirement="Day 3 must document pain outcome, mobility baseline, outstanding actions, formal closure, falls prevention plan review, and escalation if the resident has not stabilised.",
                trigger_phrases=[
                    "pain outcome",
                    "mobility",
                    "outstanding actions",
                    "closure",
                    "falls prevention plan",
                    "escalate",
                ],
                required_fields=[
                    "pain_outcome",
                    "mobility_baseline",
                    "outstanding_actions",
                    "closure",
                    "prevention_plan",
                    "escalation",
                ],
                explanation_template="Policy requires closure or escalation documentation on Day 3.",
                missing_phrases=[
                    "resolved",
                    "baseline",
                    "complete",
                    "reviewed",
                    "escalate",
                ],
                vague_phrases=["feeling well", "doing much better", "no further falls"],
            ),
        ]
