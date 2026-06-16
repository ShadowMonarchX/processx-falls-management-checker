from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

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


class ResidentNoteModel(BaseModel):
    resident_name: str
    day_label: str
    date: str
    documented_by: str
    note_text: str


class ComplianceFlagModel(BaseModel):
    day_label: str
    severity: FlagSeverity
    field: str
    explanation: str
    policy_rule_id: str
    trigger_condition: str
    evidence_found: str
    missing_requirement: str
    recommendation: str


@dataclass(frozen=True)
class ValidationEvidence:
    text: str
    matched: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    flags: list[ComplianceFlagModel] = field(default_factory=list)
    evidence: dict[str, ValidationEvidence] = field(default_factory=dict)

