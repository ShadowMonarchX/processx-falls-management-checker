import re

from src.core.models import ResidentNoteModel

# NoteAnalyzerService is a simple service that analyzes the resident notes and extracts relevant information for the LLM to process.
# It is used to analyze the resident notes and extract relevant information such as the note text and resident name, which are then passed to the LLM for processing.
# The service also includes a helper method to extract numeric scales (e.g. pain level) from the note text, which can be used by the LLM to identify specific documentation requirements related to pain assessment.
# This helps ensure that the LLM has the necessary context and information to accurately validate the resident documentation against the policy requirements and generate meaningful compliance flags and recommendations for the care team.


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
