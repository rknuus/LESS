"""Structured logging setup for the ``ebless`` logger; one JSON line per record."""

import json
import logging
import sys
from pathlib import Path

_MANAGED = "_ebless_managed"
_LOGGER_NAME = "ebless"

_STANDARD_RECORD_ATTRS = frozenset(
    vars(logging.LogRecord("", logging.NOTSET, "", 0, "", None, None)).keys()
) | {"message", "asctime", "taskName"}


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": _scalar(record.msg),
        }
        for key, value in record.__dict__.items():
            if key in _STANDARD_RECORD_ATTRS:
                continue
            payload[key] = _scalar(value)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure(level: str, log_file: Path | None) -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(_parse_level(level))
    logger.propagate = False

    _remove_managed_handlers(logger)

    formatter = StructuredFormatter()
    _attach(logger, logging.StreamHandler(sys.stderr), formatter)
    if log_file is not None:
        _attach(logger, logging.FileHandler(log_file, mode="a", encoding="utf-8"), formatter)


def _attach(logger: logging.Logger, handler: logging.Handler, formatter: logging.Formatter) -> None:
    handler.setFormatter(formatter)
    setattr(handler, _MANAGED, True)
    logger.addHandler(handler)


def _remove_managed_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        if getattr(handler, _MANAGED, False):
            logger.removeHandler(handler)
            handler.close()


def _parse_level(level: str) -> int:
    parsed = logging.getLevelName(level.upper())
    if not isinstance(parsed, int):
        raise ValueError(f"invalid log level: {level!r}")
    return parsed


def _scalar(value: object) -> object:
    if isinstance(value, str):
        return value.replace("\n", "\\n").replace("\r", "\\r")
    return value
