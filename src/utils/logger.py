import logging
from pathlib import Path


# This file defines a utility function for setting up a logger that can log messages to both the console and an optional log file.
# The logger is configured to output messages in a structured JSON format, which includes a timestamp, log level, logger name, and the log message itself.
# This allows for easy integration with logging systems that can parse JSON logs and provides a consistent logging format across the application.
def setup_logger(log_file: Path | None = None, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("processx")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter(
        fmt='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
