import json
import logging

import pytest

from ebless.logconfig import configure


@pytest.fixture(autouse=True)
def _reset_ebless_logger():
    logger = logging.getLogger("ebless")
    original_handlers = list(logger.handlers)
    original_level = logger.level
    original_propagate = logger.propagate
    yield
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    for handler in original_handlers:
        logger.addHandler(handler)
    logger.setLevel(original_level)
    logger.propagate = original_propagate


def test_configure_is_idempotent():
    configure("info", None)
    first = list(logging.getLogger("ebless").handlers)
    configure("info", None)
    second = list(logging.getLogger("ebless").handlers)
    assert len(second) == len(first)


def test_configure_does_not_remove_external_handlers():
    logger = logging.getLogger("ebless")
    foreign = logging.NullHandler()
    logger.addHandler(foreign)
    configure("info", None)
    configure("info", None)
    assert foreign in logger.handlers


@pytest.mark.parametrize("level", ["info", "INFO", "Info"])
def test_level_parsing_is_case_insensitive(level):
    configure(level, None)
    assert logging.getLogger("ebless").level == logging.INFO


def test_invalid_level_raises_value_error():
    with pytest.raises(ValueError, match="INVALID"):
        configure("INVALID", None)


def test_formatter_emits_static_msg_and_extra_fields(tmp_path, capsys):
    log_file = tmp_path / "log.jsonl"
    configure("debug", log_file)
    logging.getLogger("ebless").warning("indexed book", extra={"path": "/x", "n": 3})

    line = log_file.read_text(encoding="utf-8").splitlines()[0]
    payload = json.loads(line)
    assert payload["msg"] == "indexed book"
    assert payload["path"] == "/x"
    assert payload["n"] == 3
    assert payload["level"] == "WARNING"


def test_formatter_does_not_percent_format_msg(tmp_path):
    log_file = tmp_path / "log.jsonl"
    configure("debug", log_file)
    logging.getLogger("ebless").info("progress %s of %s", extra={"done": 1, "total": 5})

    payload = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
    assert payload["msg"] == "progress %s of %s"
    assert payload["done"] == 1
    assert payload["total"] == 5


def test_formatter_escapes_newlines_in_field_values(tmp_path):
    log_file = tmp_path / "log.jsonl"
    configure("debug", log_file)
    logging.getLogger("ebless").info("multi", extra={"detail": "line1\nline2"})

    raw = log_file.read_text(encoding="utf-8")
    assert raw.count("\n") == 1
    payload = json.loads(raw.splitlines()[0])
    assert payload["detail"] == "line1\\nline2"


def test_file_handler_appends_across_reconfiguration(tmp_path):
    log_file = tmp_path / "log.jsonl"
    logger = logging.getLogger("ebless")

    configure("info", log_file)
    logger.info("first")
    configure("info", log_file)
    logger.info("second")

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["msg"] == "first"
    assert json.loads(lines[1])["msg"] == "second"
