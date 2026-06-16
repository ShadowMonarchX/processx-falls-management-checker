from pathlib import Path
from docx import Document


class DocxParser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def paragraphs(self) -> list[str]:
        doc = Document(self.path)
        return [p.text for p in doc.paragraphs if p.text.strip()]

