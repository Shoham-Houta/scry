import pytest

from app.core import runner


def test_runner_success():
    result = runner.run(["echo", "hi"], timeout=5)
    assert result.return_code == 0


def test_runner_failure():
    result = runner.run(["eco", "hi"], timeout=5)
    assert result.return_code == -2


def test_runner_timeout():
    result = runner.run(["sleep", "5"], timeout=1)
    assert result.return_code == -1
