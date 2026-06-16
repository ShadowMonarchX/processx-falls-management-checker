import re

from src.core.models import ResidentNoteModel


class NoteAnalyzerService:
    def analyze(self, note: ResidentNoteModel) -> dict[str, str]:
        return {
            "text": note.note_text,
            "resident": note.resident_name,
        }

    @staticmethod
    def extract_numeric_scale(text: str) -> str | None:
        match = re.search(r"(\d{1,2})\s*/\s*10", text)
        return match.group(1) if match else None

