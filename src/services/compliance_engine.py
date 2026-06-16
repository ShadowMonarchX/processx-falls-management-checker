import re
from typing import Iterable

from src.core.models import (
    ComplianceFlagModel,
    FlagSeverity,
    PolicyRuleModel,
    ResidentNoteModel,
)
from src.utils.helpers import normalize_text

# ComplianceEngine is responsible for analyzing resident notes against the policy rules and generating compliance flags.
# It takes a list of PolicyRuleModel objects that represent the structured policy requirements, and evaluates
# each resident note against the relevant rules for that day. The engine generates ComplianceFlagModel objects for any compliance issues found, which include details about the issue and actionable recommendations for improvement.
# The engine's design allows for deterministic and traceable compliance checks, as each flag is directly linked to a specific policy rule and requirement.
# This helps ensure that the feedback provided to nurses is clear, actionable, and directly tied to the policy standards.
# The engine can be extended with additional rules or more complex logic as needed, while maintaining a consistent framework for compliance evaluation.


class ComplianceEngine:
    def __init__(self, rules: Iterable[PolicyRuleModel]) -> None:
        self.rules = sorted(list(rules), key=lambda rule: (rule.day, rule.rule_id))

    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        # Multiple policy rules can apply to the same note, so we evaluate every rule for the day
        # before returning flags. This avoids missing independent compliance issues.
        day_rules = [rule for rule in self.rules if rule.day == note.day_number]
        if not day_rules:
            return []
        flags: list[ComplianceFlagModel] = []
        for rule in day_rules:
            flags.extend(self._evaluate_rule(note, rule))
        return flags

    def _evaluate_rule(
        self, note: ResidentNoteModel, rule: PolicyRuleModel
    ) -> list[ComplianceFlagModel]:
        text = normalize_text(note.note_text)
        if rule.rule_id == "D1_FALL_DETAILS":
            return self._check_day1_fall_details(note, rule, text)
        if rule.rule_id == "D1_ASSESSMENT":
            return self._check_day1_assessment(note, rule, text)
        if rule.rule_id == "D1_VITALS":
            return self._check_day1_vitals(note, rule, text)
        if rule.rule_id == "D1_ACTIONS":
            return self._check_day1_actions(note, rule, text)
        if rule.rule_id == "D2_UPDATE":
            return self._check_day2(note, rule, text)
        if rule.rule_id == "D3_CLOSE":
            return self._check_day3(note, rule, text)
        return []

    def _check_day1_fall_details(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        # The sample workbook treats brief location references as sufficient if they anchor the fall
        # to a concrete place, so the check focuses on whether any location context is present.
        if not any(phrase in text for phrase in ["time of fall", "fall at", "fell at"]):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Incident timing",
                    "The date and time of fall were not documented.",
                    "Document the exact date and time of the fall.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "room",
                "corridor",
                "bathroom",
                "activity room",
                "near",
                "bedside",
                "wardrobe",
                "bed",
                "chair",
                "floor",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Location",
                    "The location of the fall was not clearly documented.",
                    "Document the location where the fall occurred.",
                )
            )
        if not any(
            phrase in text for phrase in ["witnessed", "not witnessed", "unwitnessed"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Witnessed status",
                    "Whether the fall was witnessed was not documented.",
                    "State whether the fall was witnessed or unwitnessed.",
                )
            )
        return flags

    def _check_day1_assessment(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b\d{1,2}\s*/\s*10\b", text):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Pain scale",
                    "Pain level was not recorded on the required 0-10 scale.",
                    "Document pain using a 0-10 numeric scale.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "alert",
                "orientated",
                "oriented",
                "conscious",
                "unconscious",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Consciousness",
                    "Consciousness level was not documented.",
                    "Document the resident's consciousness level.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "visible injury",
                "no visible injury",
                "laceration",
                "bruise",
                "bruising",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Visible injury",
                    "Visible injury assessment was not documented.",
                    "Document whether any visible injury is present.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "able to move all limbs",
                "move all limbs",
                "lift right arm",
                "weight-bear",
                "mobility",
                "move all limbs on request",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Limb movement",
                    "Ability to move all limbs was not documented.",
                    "Document the resident's ability to move all limbs.",
                )
            )
        return flags

    def _check_day1_vitals(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        vitals = ["bp", "hr", "rr", "temp", "temperature", "spo2"]
        if all(v not in text for v in vitals):
            return [
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Vital signs",
                    "No vital signs were documented.",
                    "Record BP, HR, RR, Temperature, and SpO2.",
                )
            ]
        # When one or more observations are present, the rule checks for the missing components
        # instead of repeating a generic "vitals missing" message.
        missing = []
        if "bp" not in text:
            missing.append("BP")
        if "hr" not in text:
            missing.append("HR")
        if "rr" not in text:
            missing.append("RR")
        if "temp" not in text and "temperature" not in text:
            missing.append("Temperature")
        if "spo2" not in text:
            missing.append("SpO2")
        if missing:
            return [
                self._flag(
                    note,
                    rule,
                    FlagSeverity.incomplete,
                    "Vital signs",
                    f"Missing vital sign components: {', '.join(missing)}.",
                    "Record a full set of observations.",
                )
            ]
        return []

    def _check_day1_actions(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        # Day 1 policy expects immediate response, escalation, family notification, and risk review.
        # Each path below maps to one of those requirements so the output stays nurse-actionable.
        if not any(
            phrase in text
            for phrase in ["immediate actions", "assisted", "call bell", "comfort"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Immediate actions",
                    "Immediate actions after the fall were not documented.",
                    "Document what immediate assistance was provided.",
                )
            )
        if "gp" in text and not any(
            phrase in text for phrase in ["notified at", "called at", "time"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "GP notification time",
                    "GP notification was documented without a time.",
                    "Record the GP name and the time of notification.",
                )
            )
        if any(
            phrase in text for phrase in ["advised to monitor", "monitor"]
        ) and not any(
            phrase in text
            for phrase in [
                "x-ray",
                "transfer",
                "threshold",
                "if pain worsens",
                "review",
                "monitor pain and mobility",
                "monitoring",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.vague,
                    "GP advice",
                    "The GP advice is too generic to act on.",
                    "Document the specific conditional advice given by the GP.",
                )
            )
        if any(
            phrase in text
            for phrase in ["family has been informed", "next of kin", "nok"]
        ) and not any(phrase in text for phrase in ["notified at", "called at"]):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "NOK notification",
                    "NOK notification was documented without a name or time.",
                    "Record the NOK name, time notified, and response.",
                )
            )
        if "care plan" in text and any(
            phrase in text for phrase in ["will update", "plan to update", "tbd"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.vague,
                    "Care plan review",
                    "The care plan update is not confirmed.",
                    "Document whether the care plan was reviewed and updated.",
                )
            )
        if not any(
            phrase in text
            for phrase in ["falls risk score", "risk score", "low", "medium", "high"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Falls risk score",
                    "Falls risk score was not reassessed.",
                    "Record the reassessed falls risk score.",
                )
            )
        if "risk factors" not in text:
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Risk factors",
                    "Risk factors were not documented.",
                    "Document the resident's fall risk factors.",
                )
            )
        return flags

    def _check_day2(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b\d{1,2}\s*/\s*10\b", text) and not any(
            phrase in text for phrase in ["improved", "worsened", "resolved"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Pain status",
                    "Current pain status was not documented.",
                    "Document whether pain improved, worsened, or resolved using the 0-10 scale.",
                )
            )
        elif any(
            phrase in text
            for phrase in ["seems okay", "doing much better", "better", "mobilising"]
        ) and not re.search(r"\b\d{1,2}\s*/\s*10\b", text):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.vague,
                    "Pain status",
                    "Pain status is described vaguely rather than clinically.",
                    "Document pain status with a numeric rating or clear clinical statement.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "weight-bear",
                "weight bear",
                "full weight-bearing",
                "full weight bear",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Mobility status",
                    "Weight-bearing status was not documented.",
                    "State clearly whether the resident can full weight-bear without pain.",
                )
            )
        elif not any(
            phrase in text
            for phrase in ["without pain", "full weight-bearing", "full weight bear"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.vague,
                    "Mobility status",
                    "Mobility status is not explicit enough.",
                    "State clearly whether the resident can full weight-bear without pain.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "new symptoms",
                "no new symptoms",
                "bruising",
                "swelling",
                "confusion",
                "behaviour",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "New symptoms",
                    "New symptoms since Day 1 were not documented.",
                    "Document whether any new symptoms appeared since Day 1.",
                )
            )
        if not any(
            phrase in text
            for phrase in ["bp", "hr", "rr", "temp", "temperature", "spo2", "vitals"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Vital signs",
                    "No full set of observations was recorded.",
                    "Record at least one full set of observations.",
                )
            )
        if not any(
            phrase in text
            for phrase in ["gp", "x-ray", "reviewed", "follow-up", "actioned"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "GP follow-up",
                    "GP follow-up was not documented.",
                    "Document whether any Day 1 GP advice was actioned.",
                )
            )
        if not any(phrase in text for phrase in ["care plan", "updated", "no changes"]):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Care plan changes",
                    "Care plan changes were not documented.",
                    "Document any changes to the care plan since Day 1.",
                )
            )
        return flags

    def _check_day3(
        self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str
    ) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        # Day 3 is a closure-or-escalation decision point, so the note must either prove recovery
        # or explicitly document why escalation is still needed.
        if not any(phrase in text for phrase in ["resolved", "ongoing"]):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Pain outcome",
                    "Pain outcome was not documented.",
                    "Document whether pain has resolved or remains ongoing with an escalation plan.",
                )
            )
        elif any(
            phrase in text for phrase in ["doing much better", "feeling well", "better"]
        ) and not any(phrase in text for phrase in ["resolved", "0/10"]):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.vague,
                    "Pain outcome",
                    "Pain outcome is vague.",
                    "State clearly whether pain is resolved, using a numeric scale if relevant.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "baseline",
                "returned to baseline",
                "full weight-bearing",
                "weight bearing",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Mobility baseline",
                    "Mobility baseline was not documented.",
                    "Confirm whether mobility has returned to baseline.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "outstanding actions",
                "no outstanding",
                "complete",
                "resolved",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Outstanding actions",
                    "Outstanding actions were not resolved or documented.",
                    "Document the resolution of any outstanding actions.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "incident closed",
                "monitoring period complete",
                "formally closed",
                "complete",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Incident closure",
                    "The incident was not formally closed.",
                    "Document that the post-fall monitoring period is complete.",
                )
            )
        if not any(
            phrase in text
            for phrase in [
                "falls prevention plan",
                "care plan",
                "reviewed",
                "discussed",
            ]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Prevention plan",
                    "The falls prevention plan was not reviewed.",
                    "Document the updated falls prevention plan review.",
                )
            )
        if not any(
            phrase in text
            for phrase in ["escalate", "escalation", "no further follow-up"]
        ):
            flags.append(
                self._flag(
                    note,
                    rule,
                    FlagSeverity.missing,
                    "Escalation",
                    "Escalation status was not documented.",
                    "Escalate if the resident has not stabilised, or document why escalation is not needed.",
                )
            )
        return flags

    def _flag(
        self,
        note: ResidentNoteModel,
        rule: PolicyRuleModel,
        severity: FlagSeverity,
        field: str,
        trigger: str,
        recommendation: str,
    ) -> ComplianceFlagModel:
        return ComplianceFlagModel(
            resident_name=note.resident_name,
            day_label=note.day_label,
            severity=severity,
            field=field,
            policy_rule_id=rule.rule_id,
            trigger_condition=trigger,
            evidence_found=note.note_text[:300],
            missing_requirement=rule.explanation_template,
            recommendation=recommendation,
        )
