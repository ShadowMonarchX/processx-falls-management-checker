from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.constants import COMPLETED_WORKBOOK_PATH, INPUT_WORKBOOK_PATH, LOGS_DIR, POLICY_PATH
from src.parsers.policy_parser import PolicyParserImpl
from src.services.compliance_engine import ComplianceEngine
from src.services.validation_engine import ValidationEngine
from src.utils.logger import setup_logger


def main() -> None:
    logger = setup_logger(LOGS_DIR / "processx.log")
    rules = PolicyParserImpl(POLICY_PATH).parse()
    logger.info("Policy loaded")
    logger.info("Rules extracted")
    engine = ComplianceEngine(rules)
    validator = ValidationEngine(INPUT_WORKBOOK_PATH, COMPLETED_WORKBOOK_PATH, engine)
    validator.run()
    logger.info("Workbook written")
    logger.info("Validation completed")


if __name__ == "__main__":
    main()
