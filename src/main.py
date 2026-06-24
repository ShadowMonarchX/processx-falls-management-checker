import sys
from pathlib import Path

# This is the main entry point of the application, which orchestrates the loading of the policy, the processing of the resident notes, and the validation of compliance against the policy rules. It sets up logging to track the progress and outcomes of each step in the process.
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.constants import (
    COMPLETED_WORKBOOK_PATH,
    INPUT_WORKBOOK_PATH,
    LOGS_DIR,
    POLICY_PATH,
)
from src.parsers.policy_parser import PolicyParserImpl
from src.services.compliance_engine import ComplianceEngine
from src.services.validation_engine import ValidationEngine
from src.core.startup import validate_startup
from src.utils.logger import setup_logger


def main() -> None:
    logger = setup_logger(LOGS_DIR / "processx.log")
    validate_startup(logger)
    logger.info("Policy loaded")
    rules = PolicyParserImpl(POLICY_PATH).parse()
    logger.info("Rules extracted")
    engine = ComplianceEngine(rules)
    validator = ValidationEngine(INPUT_WORKBOOK_PATH, COMPLETED_WORKBOOK_PATH, engine)
    logger.info("Workbook loaded")
    validator.run()
    logger.info("Workbook written")
    logger.info("Validation completed")


if __name__ == "__main__":
    main()
