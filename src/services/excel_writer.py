from pathlib import Path

from openpyxl import load_workbook

from src.core.models import ComplianceFlagModel
from src.utils.file_utils import ensure_parent


class ExcelWriter:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def open_workbook(self, source_path: Path):
        return load_workbook(source_path)

    def write_flags(self, workbook, sheet_name: str, flags: list[ComplianceFlagModel]) -> None:
        ws = workbook[sheet_name]
        start_row = ws.max_row + 1
        for idx, flag in enumerate(flags, start=start_row):
            ws[f"A{idx}"] = flag.day_label
            ws[f"B{idx}"] = flag.severity.value
            ws[f"C{idx}"] = flag.field
            ws[f"D{idx}"] = f"{flag.explanation} | Policy: {flag.policy_rule_id} | Evidence: {flag.evidence_found} | Recommendation: {flag.recommendation}"

    def save(self, workbook) -> None:
        ensure_parent(self.output_path)
        workbook.save(self.output_path)

