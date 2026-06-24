from pathlib import Path

# Keep all repository-relative paths centralized so startup validation, workbook
# generation, and documentation stay aligned even if the project is relocated.
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

# These assets are part of the contract with the workbook pipeline, so the
# paths are intentionally explicit rather than being discovered dynamically.
TASK_BRIEF_PATH = RAW_DATA_DIR / "ProcessX_AIML_Task_Brief.docx"
POLICY_PATH = RAW_DATA_DIR / "Falls_Management_Policy_ProcessX.docx"
SAMPLE_WORKBOOK_PATH = RAW_DATA_DIR / "Sample_Input_Output.xlsx"
INPUT_WORKBOOK_PATH = RAW_DATA_DIR / "Your_Output_File.xlsx"
COMPLETED_WORKBOOK_PATH = OUTPUTS_DIR / "completed_output.xlsx"
