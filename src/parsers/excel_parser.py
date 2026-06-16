from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook


@dataclass(frozen=True)
class WorkbookResidentSheet:
    input_sheet: str
    output_sheet: str
    resident_name: str


class ExcelParser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self):
        return load_workbook(self.path)

    def resident_pairs(self) -> list[WorkbookResidentSheet]:
        wb = self.load()
        pairs: list[WorkbookResidentSheet] = []
        for i in range(1, len(wb.sheetnames), 2):
            input_sheet = wb.sheetnames[i - 1]
            output_sheet = wb.sheetnames[i]
            resident_name = input_sheet.replace(" - Input", "").replace(" - Your Output", "")
            pairs.append(WorkbookResidentSheet(input_sheet, output_sheet, resident_name))
        return pairs

