from pathlib import Path

from src.parsers.excel_parser import ExcelParser


def test_excel_parser_finds_resident_pairs():
    pairs = ExcelParser(Path("data/raw/Your_Output_File.xlsx")).resident_pairs()
    assert [pair.resident_name for pair in pairs] == [
        "Alice Nguyen",
        "Robert Singh",
        "Edna Kowalski",
        "Thomas Brennan",
    ]
