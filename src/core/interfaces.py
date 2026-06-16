from typing import Protocol

from src.core.models import ComplianceFlagModel, PolicyRuleModel, ResidentNoteModel


class PolicyParser(Protocol):
    def parse(self) -> list[PolicyRuleModel]: ...


class NoteAnalyzer(Protocol):
    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]: ...

