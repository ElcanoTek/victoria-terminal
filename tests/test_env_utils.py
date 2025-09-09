import sys
from pathlib import Path

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import victoria


def test_substitute_env(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    data = {"a": "${FOO}", "b": "${MISSING}"}
    result = victoria.substitute_env(data)
    assert result["a"] == "bar"
    # missing variable remains unchanged in non-strict mode
    assert result["b"] == "${MISSING}"


def test_substitute_env_strict(monkeypatch):
    monkeypatch.delenv("BAR", raising=False)
    with pytest.raises(KeyError):
        victoria.substitute_env("${BAR}", strict=True)


def test_deep_merge():
    dst = {"a": 1, "b": {"c": 2}, "d": [1]}
    src = {"b": {"e": 3}, "d": [2, 3], "f": 4}
    merged = victoria.deep_merge(dst, src)
    assert merged == {"a": 1, "b": {"c": 2, "e": 3}, "d": [1, 2, 3], "f": 4}


def test_snowflake_env_missing(monkeypatch):
    for var in victoria.SNOWFLAKE_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    assert victoria.snowflake_env_missing() == victoria.SNOWFLAKE_ENV_VARS

