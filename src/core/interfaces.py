from typing import Protocol

from src.core.models import ComplianceFlagModel, PolicyRuleModel, ResidentNoteModel


# This file defines the interfaces for the PolicyParser and NoteAnalyzer components of the application.
# The PolicyParser interface specifies a method for parsing policy rules, while the NoteAnalyzer interface specifies
# a method for analyzing resident notes to identify compliance flags.
# These interfaces allow for the implementation of different parsing and analysis strategies while maintaining a consistent structure for the application.
class PolicyParser(Protocol):
    def parse(self) -> list[PolicyRuleModel]: ...


class NoteAnalyzer(Protocol):
    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]: ...
