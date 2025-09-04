import importlib
import sys
from pathlib import Path


def test_local_providers_merge(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("VICTORIA_HOME", raising=False)
    sys.modules.pop("victoria", None)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    victoria = importlib.import_module("victoria")
    cfg = victoria.build_crush_config(
        include_snowflake=False, strict_env=False, local_model=True
    )
    providers = cfg.get("providers", {})
    assert "openrouter" in providers
    assert "lmstudio" in providers
    assert any(
        m["id"] == "google/gemini-2.5-pro" for m in providers["openrouter"]["models"]
    )
    assert any(
        m["id"] == "openai/gpt-oss-120b" for m in providers["lmstudio"]["models"]
    )

