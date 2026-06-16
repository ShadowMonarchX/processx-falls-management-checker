import re
from typing import Iterable

from src.core.models import ComplianceFlagModel, FlagSeverity, PolicyRuleModel, ResidentNoteModel
from src.utils.helpers import contains_any, normalize_text


class ComplianceEngine:
    def __init__(self, rules: Iterable[PolicyRuleModel]) -> None:
        self.rules = list(rules)

    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        day = self._day_number(note.day_label)
        if day == 1:
            return self._check_day1(note)
        if day == 2:
            return self._check_day2(note)
        if day == 3:
            return self._check_day3(note)
        return []

    def _check_day1(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        text = note.note_text
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b\d{1,2}\s*/\s*10\b", text):
            flags.append(self._flag(note, FlagSeverity.missing, "Pain scale", "D1_PAIN", "Pain documented without numeric scale", "Numeric pain score missing", "Document the resident's pain using a 0-10 scale."))
        if not contains_any(text, ["bp", "heart rate", "hr", "rr", "spo2", "temperature"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Vital signs", "D1_VITALS", "No observation set found", "Full vital signs missing", "Record BP, HR, RR, Temperature, and SpO2."))
        if contains_any(text, ["gp notified"]) and not re.search(r"notified at", text, re.I):
            flags.append(self._flag(note, FlagSeverity.missing, "GP notification time", "D1_GP", "GP notification lacks time", "Time of notification missing", "Record the GP name, time of call, and advice given."))
        if contains_any(text, ["advised to monitor", "monitor"]) and not contains_any(text, ["x-ray", "transfer", "threshold", "if pain worsens"]):
            flags.append(self._flag(note, FlagSeverity.missing, "GP conditional actions", "D1_GP", "GP advice is too generic", "No actionable conditional advice documented", "Document the GP's specific conditional advice, such as X-ray or transfer criteria."))
        if contains_any(text, ["family has been informed", "nok", "next of kin"]) and not re.search(r"\b\w+\s*\(", text):
            flags.append(self._flag(note, FlagSeverity.missing, "NOK details", "D1_NOK", "NOK contacted without person and time", "NOK identity and time missing", "Record the NOK's name, time notified, and response."))
        if contains_any(text, ["will update", "plan to update"]):
            flags.append(self._flag(note, FlagSeverity.vague, "Care plan", "D1_CAREPLAN", "Care plan update is not confirmed", "Confirmation missing", "State explicitly whether the care plan was reviewed and updated: Yes or No."))
        if not contains_any(text, ["falls risk score", "risk score", "high", "medium", "low"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Falls risk score", "D1_RISK", "Risk score absent", "Risk score missing", "Document the reassessed falls risk score."))
        return flags

    def _check_day2(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        text = normalize_text(note.note_text)
        flags: list[ComplianceFlagModel] = []
        if not re.search(r"\b(\d{1,2})\s*/\s*10\b", text) and not contains_any(text, ["improved", "worsened", "resolved"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Pain status", "D2_UPDATE", "Pain status not updated", "Pain update missing", "Document whether pain improved, worsened, or resolved using the 0-10 scale."))
        if not contains_any(text, ["weight-bear", "weight bear", "mobility", "mobilising", "walking"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Mobility status", "D2_UPDATE", "Mobility status absent", "Mobility not documented", "State whether the resident can full weight-bear without pain."))
        elif not contains_any(text, ["without pain", "full weight-bear", "full weight bear"]):
            flags.append(self._flag(note, FlagSeverity.vague, "Mobility status", "D2_UPDATE", "Mobility is described indirectly", "Weight-bearing status unclear", "State clearly whether the resident can full weight-bear without pain."))
        if not contains_any(text, ["bp", "hr", "rr", "temp", "spo2", "vitals"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Vital signs", "D2_UPDATE", "No observation set found", "Vitals missing", "Record at least one full set of observations."))
        if not contains_any(text, ["new symptoms", "bruising", "swelling", "confusion", "behaviour"]):
            flags.append(self._flag(note, FlagSeverity.missing, "New symptoms", "D2_UPDATE", "New symptoms not assessed", "Assessment missing", "Document whether any new symptoms have appeared since Day 1."))
        if not contains_any(text, ["gp", "reviewed", "x-ray", "follow-up", "actioned"]):
            flags.append(self._flag(note, FlagSeverity.missing, "GP follow-up", "D2_UPDATE", "GP follow-up not documented", "GP follow-up missing", "Document whether any Day 1 GP advice has been actioned."))
        if not contains_any(text, ["care plan", "no changes", "updated"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Care plan changes", "D2_UPDATE", "Care plan change not documented", "Care plan update missing", "Document any changes to the care plan since Day 1."))
        return flags

    def _check_day3(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]:
        text = normalize_text(note.note_text)
        flags: list[ComplianceFlagModel] = []
        if not contains_any(text, ["resolved", "ongoing", "pain outcome"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Pain outcome", "D3_CLOSE", "Pain outcome absent", "Pain outcome missing", "Document whether pain has resolved or remains ongoing with escalation."))
        elif contains_any(text, ["doing much better", "feeling well", "better"]) and not contains_any(text, ["resolved", "0/10"]):
            flags.append(self._flag(note, FlagSeverity.vague, "Pain outcome", "D3_CLOSE", "Pain outcome is vague", "Clinical resolution not confirmed", "State clearly whether pain is resolved, using a numeric scale if relevant."))
        if not contains_any(text, ["baseline", "returned to baseline", "full weight-bearing", "weight bearing"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Mobility baseline", "D3_CLOSE", "Baseline mobility not documented", "Mobility closure missing", "Confirm whether mobility has returned to baseline."))
        if not contains_any(text, ["incident closed", "monitoring period complete", "formal closure", "complete"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Incident closure", "D3_CLOSE", "Closure statement missing", "Incident not formally closed", "Document that the post-fall monitoring period is complete."))
        if not contains_any(text, ["falls prevention plan", "care plan", "reviewed", "discussed"]):
            flags.append(self._flag(note, FlagSeverity.missing, "Falls prevention plan", "D3_CLOSE", "Prevention plan review missing", "Prevention plan not reviewed", "Document the updated falls prevention plan review."))
        return flags

    def _flag(self, note: ResidentNoteModel, severity: FlagSeverity, field: str, rule_id: str, trigger: str, missing: str, recommendation: str) -> ComplianceFlagModel:
        return ComplianceFlagModel(
            day_label=note.day_label,
            severity=severity,
            field=field,
            explanation=missing,
            policy_rule_id=rule_id,
            trigger_condition=trigger,
            evidence_found=note.note_text[:260],
            missing_requirement=rule_id,
            recommendation=recommendation,
        )

    @staticmethod
    def _day_number(day_label: str) -> int:
        match = re.search(r"(\d+)", day_label)
        return int(match.group(1)) if match else 0

