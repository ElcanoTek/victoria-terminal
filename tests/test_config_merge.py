import sys
from pathlib import Path

# Add project root to path to allow importing scripts
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from VictoriaTerminal import build_crush_config


def test_local_providers_merge(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("VICTORIA_HOME", raising=False)

    cfg = build_crush_config(
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
