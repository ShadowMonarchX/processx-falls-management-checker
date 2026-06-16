from pathlib import Path

from src.core.exceptions import WorkbookError
from src.core.models import ResidentNoteModel
from src.services.compliance_engine import ComplianceEngine
from src.services.excel_writer import ExcelWriter


class ValidationEngine:
    def __init__(self, source_workbook: Path, output_workbook: Path, compliance_engine: ComplianceEngine) -> None:
        self.source_workbook = source_workbook
        self.output_workbook = output_workbook
        self.compliance_engine = compliance_engine

    def run(self) -> None:
        writer = ExcelWriter(self.output_workbook)
        workbook = writer.open_workbook(self.source_workbook)
        for sheet_name in workbook.sheetnames:
            if not sheet_name.endswith(" - Input"):
                continue
            resident_name = sheet_name[: -len(" - Input")]
            output_sheet = f"{resident_name} - Your Output"
            if output_sheet not in workbook.sheetnames:
                raise WorkbookError(f"Output sheet missing for resident: {resident_name}")
            flags = self._analyze_resident_sheet(workbook[sheet_name], resident_name)
            writer.write_flags(workbook, output_sheet, flags)
        writer.save(workbook)

    def _analyze_resident_sheet(self, worksheet, resident_name: str):
        flags = []
        for row in range(4, worksheet.max_row + 1):
            day = worksheet[f"A{row}"].value
            date = worksheet[f"B{row}"].value
            documented_by = worksheet[f"C{row}"].value
            note_text = worksheet[f"D{row}"].value
            if not day or not note_text:
                continue
            note = ResidentNoteModel(
                resident_name=resident_name,
                day_label=str(day),
                date=str(date or ""),
                documented_by=str(documented_by or ""),
                note_text=str(note_text or ""),
            )
            flags.extend(self.compliance_engine.analyze(note))
        return flags
