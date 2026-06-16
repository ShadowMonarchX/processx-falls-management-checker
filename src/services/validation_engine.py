from pathlib import Path

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
        wb = writer.open_workbook(self.source_workbook)
        for sheet_name in wb.sheetnames:
            if not sheet_name.endswith(" - Input"):
                continue
            resident_name = sheet_name.replace(" - Input", "")
            input_sheet = wb[sheet_name]
            flags = []
            for row in range(4, input_sheet.max_row + 1):
                day = input_sheet[f"A{row}"].value
                date = input_sheet[f"B{row}"].value
                documented_by = input_sheet[f"C{row}"].value
                note_text = input_sheet[f"D{row}"].value
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
            output_sheet = f"{resident_name} - Your Output" if f"{resident_name} - Your Output" in wb.sheetnames else f"{resident_name} - Output"
            writer.write_flags(wb, output_sheet, flags)
        writer.save(wb)
