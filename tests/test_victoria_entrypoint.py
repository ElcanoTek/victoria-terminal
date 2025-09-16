import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from victoria_entrypoint import (
    CRUSH_TEMPLATE,
    ENV_FILENAME,
    resource_path,
    generate_crush_config,
    ensure_configuration,
    parse_env_file,
    sync_shared_configuration,
    write_env_file,
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


def test_write_env_file_orders_keys(tmp_path: Path) -> None:
    env_path = tmp_path / ENV_FILENAME
    values = {
        "OPENROUTER_API_KEY": "abc123",
        "SNOWFLAKE_ACCOUNT": "my-account",
        "OTHER": "value",
    }

    write_env_file(env_path, values)

    content = env_path.read_text(encoding="utf-8").splitlines()
    assert content[0] == "# Victoria environment configuration"
    assert content[2] == 'OPENROUTER_API_KEY="abc123"'
    assert content[3] == 'SNOWFLAKE_ACCOUNT="my-account"'
    assert content[7] == "SNOWFLAKE_ROLE="
    assert content[-1] == 'OTHER="value"'


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
    args = data["mcp"]["snowflake"]["args"]
    for value in ("acct", "user", "password", "warehouse", "role"):
        assert value in args
    assert str(tmp_path / "adtech.duckdb") in data["mcp"]["motherduck"]["args"]


def test_ensure_configuration_requires_interactive(tmp_path: Path, mocker) -> None:
    mock_warn = mocker.Mock()
    home = tmp_path / "Victoria"
    home.mkdir()

    mocker.patch("victoria_entrypoint.warn", mock_warn)
    configured = ensure_configuration(interactive=False, app_home=home)

    assert configured is False
    mock_warn.assert_called_once()
    assert not (home / ENV_FILENAME).exists()


def test_sync_shared_configuration_copies_files(tmp_path: Path) -> None:
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / ENV_FILENAME).write_text("OPENROUTER_API_KEY=shared\n", encoding="utf-8")

    local = tmp_path / "local"
    copied = sync_shared_configuration(shared, local_home=local)

    assert copied == [local / ENV_FILENAME]
    assert (local / ENV_FILENAME).read_text(encoding="utf-8") == "OPENROUTER_API_KEY=shared\n"
