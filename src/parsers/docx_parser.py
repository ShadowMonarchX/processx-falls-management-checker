from pathlib import Path

from docx import Document


# DocxParser is a simple parser for .docx files that extracts the text from the paragraphs.
# It is used to extract the text from the resident's input document, which is then processed by the LLM.
class DocxParser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def paragraphs(self) -> list[str]:
        doc = Document(self.path)
        return [p.text for p in doc.paragraphs if p.text.strip()]
