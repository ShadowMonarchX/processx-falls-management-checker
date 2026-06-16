import re
from typing import Iterable

from src.core.models import ComplianceFlagModel, FlagSeverity, PolicyRuleModel, ResidentNoteModel
from src.utils.helpers import contains_any, normalize_text


class ComplianceEngine:
    def __init__(self, rules: Iterable[PolicyRuleModel]) -> None:
        self.rules = sorted(list(rules), key=lambda rule: (rule.day, rule.rule_id))

    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        day_rules = [rule for rule in self.rules if rule.day == note.day_number]
        if not day_rules:
            return []
        flags: list[ComplianceFlagModel] = []
        for rule in day_rules:
            flags.extend(self._evaluate_rule(note, rule))
        return flags

    def _evaluate_rule(self, note: ResidentNoteModel, rule: PolicyRuleModel) -> list[ComplianceFlagModel]:
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

    def _check_day1_fall_details(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not contains_any(text, ["time of fall", "fall at", "fell at"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Incident timing", "The date and time of fall were not documented.", "Document the exact date and time of the fall."))
        if not contains_any(text, ["room", "corridor", "bathroom", "activity room", "near", "bedside", "wardrobe"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Location", "The location of the fall was not clearly documented.", "Document the location where the fall occurred."))
        if not contains_any(text, ["witnessed", "not witnessed", "unwitnessed"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Witnessed status", "Whether the fall was witnessed was not documented.", "State whether the fall was witnessed or unwitnessed."))
        return flags

    def _check_day1_assessment(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b\d{1,2}\s*/\s*10\b", text):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Pain scale", "Pain level was not recorded on the required 0-10 scale.", "Document pain using a 0-10 numeric scale."))
        if not contains_any(text, ["alert", "orientated", "oriented", "conscious", "unconscious"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Consciousness", "Consciousness level was not documented.", "Document the resident's consciousness level."))
        if not contains_any(text, ["visible injury", "no visible injury", "laceration", "bruise", "bruising"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Visible injury", "Visible injury assessment was not documented.", "Document whether any visible injury is present."))
        if not contains_any(text, ["able to move all limbs", "move all limbs", "lift right arm", "weight-bear", "mobility"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Limb movement", "Ability to move all limbs was not documented.", "Document the resident's ability to move all limbs."))
        return flags

    def _check_day1_vitals(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        vitals = ["bp", "hr", "rr", "temp", "temperature", "spo2"]
        if all(not contains_any(text, [v]) for v in vitals):
            return [self._flag(note, rule, FlagSeverity.missing, "Vital signs", "No vital signs were documented.", "Record BP, HR, RR, Temperature, and SpO2.")]
        missing = [label for label in ["BP", "HR", "RR", "Temperature", "SpO2"] if not contains_any(text, [label.lower()])]
        if missing:
            return [self._flag(note, rule, FlagSeverity.incomplete, "Vital signs", f"Missing vital sign components: {', '.join(missing)}.", "Record a full set of observations.")]
        return []

    def _check_day1_actions(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not contains_any(text, ["immediate actions", "assisted", "call bell", "comfort"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Immediate actions", "Immediate actions after the fall were not documented.", "Document what immediate assistance was provided."))
        if contains_any(text, ["gp"]) and not contains_any(text, ["notified at", "called at", "time"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "GP notification time", "GP notification was documented without a time.", "Record the GP name and the time of notification."))
        if contains_any(text, ["advised to monitor", "monitor"]) and not contains_any(text, ["x-ray", "transfer", "threshold", "if pain worsens", "review"]):
            flags.append(self._flag(note, rule, FlagSeverity.vague, "GP advice", "The GP advice is too generic to act on.", "Document the specific conditional advice given by the GP."))
        if contains_any(text, ["family has been informed", "next of kin", "nok"]) and not contains_any(text, ["notified at", "called at"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "NOK notification", "NOK notification was documented without a name or time.", "Record the NOK name, time notified, and response."))
        if contains_any(text, ["will update", "update", "plan to update"]) and not contains_any(text, ["yes", "no"]):
            flags.append(self._flag(note, rule, FlagSeverity.vague, "Care plan review", "The care plan update is not confirmed.", "Document whether the care plan was reviewed and updated."))
        if not contains_any(text, ["falls risk score", "risk score", "low", "medium", "high"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Falls risk score", "Falls risk score was not reassessed.", "Record the reassessed falls risk score."))
        if not contains_any(text, ["risk factors"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Risk factors", "Risk factors were not documented.", "Document the resident's fall risk factors."))
        return flags

    def _check_day2(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b\d{1,2}\s*/\s*10\b", text) and not contains_any(text, ["improved", "worsened", "resolved"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Pain status", "Current pain status was not documented.", "Document whether pain improved, worsened, or resolved using the 0-10 scale."))
        elif contains_any(text, ["seems okay", "doing much better", "better", "mobilising"]) and not re.search(r"\b\d{1,2}\s*/\s*10\b", text):
            flags.append(self._flag(note, rule, FlagSeverity.vague, "Pain status", "Pain status is described vaguely rather than clinically.", "Document pain status with a numeric rating or clear clinical statement."))
        if not contains_any(text, ["weight-bear", "weight bear", "full weight-bearing", "full weight bear"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Mobility status", "Weight-bearing status was not documented.", "State clearly whether the resident can full weight-bear without pain."))
        elif not contains_any(text, ["without pain", "full weight-bearing", "full weight bear"]):
            flags.append(self._flag(note, rule, FlagSeverity.vague, "Mobility status", "Mobility status is not explicit enough.", "State clearly whether the resident can full weight-bear without pain."))
        if not contains_any(text, ["new symptoms", "no new symptoms", "bruising", "swelling", "confusion", "behaviour"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "New symptoms", "New symptoms since Day 1 were not documented.", "Document whether any new symptoms appeared since Day 1."))
        if not contains_any(text, ["bp", "hr", "rr", "temp", "temperature", "spo2", "vitals"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Vital signs", "No full set of observations was recorded.", "Record at least one full set of observations."))
        if not contains_any(text, ["gp", "x-ray", "reviewed", "follow-up", "actioned"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "GP follow-up", "GP follow-up was not documented.", "Document whether any Day 1 GP advice was actioned."))
        if not contains_any(text, ["care plan", "updated", "no changes"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Care plan changes", "Care plan changes were not documented.", "Document any changes to the care plan since Day 1."))
        return flags

    def _check_day3(self, note: ResidentNoteModel, rule: PolicyRuleModel, text: str) -> list[ComplianceFlagModel]:
        flags: list[ComplianceFlagModel] = []
        if not contains_any(text, ["resolved", "ongoing"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Pain outcome", "Pain outcome was not documented.", "Document whether pain has resolved or remains ongoing with an escalation plan."))
        elif contains_any(text, ["doing much better", "feeling well", "better"]) and not contains_any(text, ["resolved", "0/10"]):
            flags.append(self._flag(note, rule, FlagSeverity.vague, "Pain outcome", "Pain outcome is vague.", "State clearly whether pain is resolved, using a numeric scale if relevant."))
        if not contains_any(text, ["baseline", "returned to baseline", "full weight-bearing", "weight bearing"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Mobility baseline", "Mobility baseline was not documented.", "Confirm whether mobility has returned to baseline."))
        if not contains_any(text, ["outstanding actions", "no outstanding", "complete", "resolved"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Outstanding actions", "Outstanding actions were not resolved or documented.", "Document the resolution of any outstanding actions."))
        if not contains_any(text, ["incident closed", "monitoring period complete", "formally closed", "complete"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Incident closure", "The incident was not formally closed.", "Document that the post-fall monitoring period is complete."))
        if not contains_any(text, ["falls prevention plan", "care plan", "reviewed", "discussed"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Prevention plan", "The falls prevention plan was not reviewed.", "Document the updated falls prevention plan review."))
        if not contains_any(text, ["escalate", "escalation", "no further follow-up"]):
            flags.append(self._flag(note, rule, FlagSeverity.missing, "Escalation", "Escalation status was not documented.", "Escalate if the resident has not stabilised, or document why escalation is not needed."))
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
