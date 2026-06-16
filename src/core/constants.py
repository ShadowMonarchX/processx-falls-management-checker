from pathlib import Path

# This file defines constants for the project, including directory paths and file paths for raw data, processed data, outputs, logs, and specific documents related to the falls management policy.
# These constants are used throughout the project to ensure consistency and ease of maintenance when accessing these resources.

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

# File paths for specific documents and workbooks used in the project

TASK_BRIEF_PATH = RAW_DATA_DIR / "ProcessX_AIML_Task_Brief.docx"
POLICY_PATH = RAW_DATA_DIR / "Falls_Management_Policy_ProcessX.docx"
SAMPLE_WORKBOOK_PATH = RAW_DATA_DIR / "Sample_Input_Output.xlsx"
INPUT_WORKBOOK_PATH = RAW_DATA_DIR / "Your_Output_File.xlsx"
COMPLETED_WORKBOOK_PATH = OUTPUTS_DIR / "completed_output.xlsx"
