import json
import logging

import pytest
from click.testing import CliRunner

from ebless.cli import cli


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


def test_log_level_debug_accepted(tmp_path):
    result = CliRunner().invoke(
        cli, ["--log-level", "DEBUG", "index", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert logging.getLogger("ebless").level == logging.DEBUG


def test_log_level_invalid_rejected(tmp_path):
    result = CliRunner().invoke(
        cli, ["--log-level", "INVALID", "index", str(tmp_path)]
    )
    assert result.exit_code != 0
    assert "Invalid value" in result.stderr
    assert "INVALID" in result.stderr


def test_log_file_appends_across_invocations(tmp_path):
    log_file = tmp_path / "log.jsonl"
    runner = CliRunner()

    first = runner.invoke(cli, ["--log-file", str(log_file), "index", str(tmp_path)])
    assert first.exit_code == 0
    logging.getLogger("ebless").info("first record")

    second = runner.invoke(cli, ["--log-file", str(log_file), "index", str(tmp_path)])
    assert second.exit_code == 0
    logging.getLogger("ebless").info("second record")

    lines = log_file.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]
    messages = [payload["msg"] for payload in payloads]
    assert "first record" in messages
    assert "second record" in messages


def test_default_invocation_configures_structured_stderr_handler(tmp_path):
    result = CliRunner().invoke(cli, ["index", str(tmp_path)])
    assert result.exit_code == 0

    logger = logging.getLogger("ebless")
    assert logger.level == logging.INFO

    stream_handlers = [
        h for h in logger.handlers if type(h) is logging.StreamHandler
    ]
    assert len(stream_handlers) == 1
    handler = stream_handlers[0]

    record = logger.makeRecord("ebless", logging.INFO, "", 0, "hello", (), None)
    payload = json.loads(handler.format(record))
    assert payload["msg"] == "hello"
    assert payload["level"] == "INFO"
