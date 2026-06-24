from typing import Protocol

from src.core.models import ComplianceFlagModel, PolicyRuleModel, ResidentNoteModel


# Protocols keep the parser and analyzer layers swappable without forcing a
# concrete inheritance tree, which is useful when the AI backend changes.
class PolicyParser(Protocol):
    def parse(self) -> list[PolicyRuleModel]: ...


class NoteAnalyzer(Protocol):
    # The analyzer contract returns flags rather than raw model text so the
    # compliance engine can remain deterministic and testable.
    def analyze(self, note: ResidentNoteModel) -> list[ComplianceFlagModel]: ...
