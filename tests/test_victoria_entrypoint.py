import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from victoria_entrypoint import (  # noqa: E402
    CRUSH_TEMPLATE,
    ENV_FILENAME,
    generate_crush_config,
    load_environment,
    parse_env_file,
    resource_path,
)


def test_parse_env_file_handles_comments(tmp_path: Path) -> None:
    env_path = tmp_path / ENV_FILENAME
    env_path.write_text(
        "FOO=bar\n"
        "# comment\n"
        "MALFORMED\n"
        'QUOTED="some value"\n',
        encoding="utf-8",
    )

    values = parse_env_file(env_path)

    assert values["FOO"] == "bar"
    assert values["QUOTED"] == "some value"
    assert "MALFORMED" not in values


def test_load_environment_preserves_existing_values(tmp_path: Path) -> None:
    env_path = tmp_path / ENV_FILENAME
    env_path.write_text("FOO=bar\nSHARED=value\n", encoding="utf-8")

    custom_env = {"SHARED": "existing"}

    values = load_environment(app_home=tmp_path, env=custom_env)

    assert values == {"FOO": "bar", "SHARED": "value"}
    assert custom_env["FOO"] == "bar"
    assert custom_env["SHARED"] == "existing"


def test_generate_crush_config_substitutes_env(tmp_path: Path) -> None:
    env_values = {
        "OPENROUTER_API_KEY": "test-key",
        "SNOWFLAKE_ACCOUNT": "acct",
        "SNOWFLAKE_USER": "user",
        "SNOWFLAKE_PASSWORD": "password",
        "SNOWFLAKE_WAREHOUSE": "warehouse",
        "SNOWFLAKE_ROLE": "role",
        "VICTORIA_HOME": str(tmp_path),
    }

    template = resource_path(CRUSH_TEMPLATE)
    output = generate_crush_config(app_home=tmp_path, env=env_values, template_path=template)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["providers"]["openrouter"]["api_key"] == "test-key"
    motherduck = data["mcp"]["motherduck"]
    assert motherduck["command"] == "python"
    assert motherduck["args"][:2] == ["-m", "mcp_server_motherduck"]
    assert str(tmp_path / "adtech.duckdb") in motherduck["args"]

    snowflake = data["mcp"]["snowflake"]
    assert snowflake["command"] == "python"
    assert snowflake["args"][:2] == ["-m", "mcp_snowflake_server"]
    for value in ("acct", "user", "password", "warehouse", "role"):
        assert value in snowflake["args"]
