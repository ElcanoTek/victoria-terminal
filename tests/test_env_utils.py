import sys
from pathlib import Path

import pytest

# Add project root to path to allow importing victoria
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from VictoriaTerminal import substitute_env, deep_merge, SNOWFLAKE_ENV_VARS, snowflake_env_missing


def test_substitute_env(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    data = {"a": "${FOO}", "b": "${MISSING}"}
    result = substitute_env(data)
    assert result["a"] == "bar"
    # missing variable remains unchanged in non-strict mode
    assert result["b"] == "${MISSING}"


def test_substitute_env_strict(monkeypatch):
    monkeypatch.delenv("BAR", raising=False)
    with pytest.raises(KeyError):
        substitute_env("${BAR}", strict=True)


def test_deep_merge():
    dst = {"a": 1, "b": {"c": 2}, "d": [1]}
    src = {"b": {"e": 3}, "d": [2, 3], "f": 4}
    merged = deep_merge(dst, src)
    assert merged == {"a": 1, "b": {"c": 2, "e": 3}, "d": [1, 2, 3], "f": 4}


def test_snowflake_env_missing(monkeypatch):
    for var in SNOWFLAKE_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    assert snowflake_env_missing() == SNOWFLAKE_ENV_VARS

