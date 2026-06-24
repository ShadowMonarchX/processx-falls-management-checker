import logging
import json
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
            }:
                continue
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def setup_logger(log_file: Path | None = None, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("processx")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        formatter = JsonFormatter()
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        logger.addHandler(stream)

    if log_file is not None and not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file
        for handler in logger.handlers
    ):
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger
