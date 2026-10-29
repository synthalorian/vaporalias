import io

from vaporalias.cli import main
from vaporalias.color import Palette, color_enabled

from fakes import TTYBuffer

ARGS = ["--alias", "example_alias", "--name", "Jane Placeholder", "--i-am-this-person"]


def test_color_on_for_tty_without_no_color():
    assert color_enabled(TTYBuffer(True), environ={}) is True


def test_no_color_env_disables_even_on_tty():
    assert color_enabled(TTYBuffer(True), environ={"NO_COLOR": "1"}) is False


def test_no_color_empty_value_is_ignored():
    assert color_enabled(TTYBuffer(True), environ={"NO_COLOR": ""}) is True


def test_no_color_empty_value_still_respects_non_tty():
    assert color_enabled(io.StringIO(), environ={"NO_COLOR": ""}) is False


def test_non_tty_disables():
    assert color_enabled(io.StringIO(), environ={}) is False
    assert color_enabled(TTYBuffer(False), environ={}) is False


def test_palette_disabled_is_passthrough():
    p = Palette(False)
    assert p.cyan("x") == "x"
    assert p.magenta("x") == "x"
    assert p.title("x") == "x"


def test_palette_enabled_wraps_in_ansi():
    s = Palette(True).cyan("x")
    assert s.startswith("\033[") and s.endswith("\033[0m") and "x" in s


def test_cli_output_has_no_ansi_when_not_tty():
    buf = io.StringIO()
    main(ARGS, out=buf, environ={})
    assert "\033[" not in buf.getvalue()


def test_cli_output_has_no_ansi_with_no_color_on_tty():
    buf = TTYBuffer(True)
    main(ARGS, out=buf, environ={"NO_COLOR": "1"})
    assert "\033[" not in buf.getvalue()


def test_cli_output_colored_on_tty_with_empty_no_color():
    buf = TTYBuffer(True)
    main(ARGS, out=buf, environ={"NO_COLOR": ""})
    assert "\033[96m" in buf.getvalue()


def test_cli_output_colored_on_tty():
    buf = TTYBuffer(True)
    main(ARGS, out=buf, environ={})
    assert "\033[96m" in buf.getvalue()
    assert "\033[95m" in buf.getvalue()
