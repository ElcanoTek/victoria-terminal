from VictoriaTerminal import course_menu, local_model_menu
from victoria_entrypoint import prompt_for_configuration, SNOWFLAKE_ENV_VARS


def test_local_model_menu_yes(mocker):
    mocker.patch("rich.prompt.Prompt.ask", return_value="y")
    assert local_model_menu() is True


def test_local_model_menu_no(mocker):
    mocker.patch("rich.prompt.Prompt.ask", return_value="n")
    assert local_model_menu() is False


def test_course_menu_one(mocker):
    mocker.patch("rich.prompt.Prompt.ask", return_value="1")
    assert course_menu() == "1"


def test_course_menu_two(mocker):
    mocker.patch("rich.prompt.Prompt.ask", return_value="2")
    assert course_menu() == "2"


def test_prompt_for_configuration_openrouter_retry(mocker):
    confirm = mocker.Mock(side_effect=[True, False])
    prompt = mocker.Mock(side_effect=["", "api-key"])
    warn = mocker.Mock()

    result = prompt_for_configuration(
        {},
        _Confirm_ask=confirm,
        _Prompt_ask=prompt,
        _section=mocker.Mock(),
        _info=mocker.Mock(),
        _warn=warn,
    )

    assert result["OPENROUTER_API_KEY"] == "api-key"
    warn.assert_called_once()
    prompt.assert_called()


def test_prompt_for_configuration_decline_all(mocker):
    confirm = mocker.Mock(side_effect=[False, False])

    result = prompt_for_configuration(
        {"OPENROUTER_API_KEY": "previous"},
        _Confirm_ask=confirm,
        _Prompt_ask=mocker.Mock(),
        _section=mocker.Mock(),
        _info=mocker.Mock(),
        _warn=mocker.Mock(),
    )

    assert "OPENROUTER_API_KEY" not in result
    for key in SNOWFLAKE_ENV_VARS:
        assert key not in result


def test_prompt_for_configuration_snowflake(mocker):
    confirm = mocker.Mock(side_effect=[False, True])
    responses = [f"value-{i}" for i in range(len(SNOWFLAKE_ENV_VARS))]
    prompt = mocker.Mock(side_effect=responses)

    result = prompt_for_configuration(
        {},
        _Confirm_ask=confirm,
        _Prompt_ask=prompt,
        _section=mocker.Mock(),
        _info=mocker.Mock(),
        _warn=mocker.Mock(),
    )

    for key, expected in zip(SNOWFLAKE_ENV_VARS, responses):
        assert result[key] == expected
