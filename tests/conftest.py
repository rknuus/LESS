import logging

import pytest


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


@pytest.fixture(autouse=True)
def _redirect_inventory_path(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ebless.inventory.INVENTORY_PATH",
        tmp_path / "inventory.json",
    )
