import sys
from pathlib import Path

# Bootstrap the repository root before imports so the same entrypoint works
# both from the checkout and from a packaged or virtualenv execution context.
if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parents[1]
    venv_site_packages = repo_root / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if venv_site_packages.exists():
        sys.path.insert(0, str(venv_site_packages))
    sys.path.append(str(repo_root))

from src.core.environment import apply_env_file

apply_env_file(repo_root / ".env")

from src.core.constants import (
    COMPLETED_WORKBOOK_PATH,
    INPUT_WORKBOOK_PATH,
    LOGS_DIR,
    POLICY_PATH,
)
from src.ai.health import log_provider_diagnostics
from src.parsers.policy_parser import PolicyParserImpl
from src.services.compliance_engine import ComplianceEngine
from src.services.validation_engine import ValidationEngine
from src.core.startup import validate_startup
from src.utils.logger import setup_logger


def main() -> None:
    # The health-check path is intentionally side-effect light so operators can
    # validate configuration without triggering workbook processing.
    if "--health-check" in sys.argv:
        logger = setup_logger(LOGS_DIR / "processx.log")
        validate_startup(logger)
        log_provider_diagnostics(logger)
        print("Provider Status")
        print("---------------")
        from src.ai.health import provider_diagnostics

        for diag in provider_diagnostics():
            if diag["provider"] == "local_gguf":
                status = "HEALTHY" if diag["healthy"] else "UNHEALTHY"
                print(f"Local GGUF : {status}")
            elif diag["provider"] == "gemini":
                status = "HEALTHY" if diag["healthy"] else "MISSING KEY"
                print(f"Gemini     : {status}")
            elif diag["provider"] == "claude":
                status = "HEALTHY" if diag["healthy"] else "MISSING KEY"
                print(f"Claude     : {status}")
            elif diag["provider"] == "openai":
                status = "HEALTHY" if diag["healthy"] else "MISSING KEY"
                print(f"OpenAI     : {status}")
            elif diag["provider"] == "ollama":
                status = "HEALTHY" if diag["healthy"] else "NOT INSTALLED"
                print(f"Ollama     : {status}")
        return
    logger = setup_logger(LOGS_DIR / "processx.log")
    validate_startup(logger)
    log_provider_diagnostics(logger)
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
