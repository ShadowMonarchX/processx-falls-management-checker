from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FlagSeverity(str, Enum):
    missing = "Missing"
    vague = "Vague"
    incomplete = "Incomplete"
    non_compliant = "Non-compliant"
    complete = "Complete"


class PolicyRuleModel(BaseModel):
    rule_id: str
    day: int
    requirement: str
    trigger_phrases: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    explanation_template: str
    missing_phrases: list[str] = Field(default_factory=list)
    vague_phrases: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


class ResidentNoteModel(BaseModel):
    resident_name: str
    day_label: str
    date: str
    documented_by: str
    note_text: str

    @property
    def day_number(self) -> int:
        import re

        match = re.search(r"(\d+)", self.day_label)
        return int(match.group(1)) if match else 0


class ComplianceFlagModel(BaseModel):
    resident_name: str
    day_label: str
    severity: FlagSeverity
    field: str
    policy_rule_id: str
    trigger_condition: str
    evidence_found: str
    missing_requirement: str
    recommendation: str

    @property
    def explanation(self) -> str:
        return self.missing_requirement


@dataclass(frozen=True)
class ValidationEvidence:
    text: str
    matched: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    flags: list[ComplianceFlagModel] = field(default_factory=list)
    evidence: dict[str, ValidationEvidence] = field(default_factory=dict)
