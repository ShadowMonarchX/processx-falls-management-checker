from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# This file defines the core data models used in the falls management checker application.
# It includes models for representing policy rules, resident notes, compliance flags, and validation results. These models are designed to be flexible and extensible, allowing for easy integration with various components of the application such as the AI module and the data processing pipeline.


class FlagSeverity(str, Enum):
    missing = "Missing"
    vague = "Vague"
    incomplete = "Incomplete"
    non_compliant = "Non-compliant"
    complete = "Complete"


# The PolicyRuleModel represents a single rule from the falls management policy, including its ID, requirement text, trigger phrases, required and optional fields, explanation template, and examples.
# This model is used to structure the policy rules in a way that can be easily processed and analyzed by the application.


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


# The ResidentNoteModel represents a note documented for a resident, including the resident's name, the day label, the date of the note, who documented it, and the text of the note itself. It also includes a property to extract the day number from the day label for easier processing.


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


# The ComplianceFlagModel represents a flag raised for a resident based on the analysis of their notes against the policy rules.
# It includes details such as the resident's name, the day label, the severity of the flag, the field that triggered the flag, the associated policy rule ID, the trigger condition, evidence found, missing requirements, and recommendations.
# It also has a property to provide an explanation based on the missing requirement.


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


# The ValidationEvidence and ValidationResult models are used to structure the results of validating resident notes against the policy rules.
# ValidationEvidence captures the text of the evidence, whether it matched the expected criteria, and any additional details.
# ValidationResult aggregates the compliance flags raised and the evidence collected during the validation process, allowing for a comprehensive overview of the validation outcomes for each resident and day.
@dataclass(frozen=True)
class ValidationEvidence:
    text: str
    matched: bool
    details: dict[str, Any] = field(default_factory=dict)


# The ValidationResult model aggregates the compliance flags raised and the evidence collected during the validation process, allowing for a comprehensive overview of the validation outcomes for each resident and day.


@dataclass(frozen=True)
class ValidationResult:
    flags: list[ComplianceFlagModel] = field(default_factory=list)
    evidence: dict[str, ValidationEvidence] = field(default_factory=dict)
