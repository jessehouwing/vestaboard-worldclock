"""Tests for the World Clock plugin."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import pytz

from src.devices import BoardContext

from plugins import vestaboard_worldclock as wc

MANIFEST = json.loads((Path(__file__).parent.parent / "manifest.json").read_text())

CONFIG = {
    "name_1": "Home", "timezone_1": "Europe/Amsterdam",
    "name_2": "Papa", "timezone_2": "America/Los_Angeles",
    "name_3": "Tokyo", "timezone_3": "Asia/Tokyo",
}


def make(config, board=None):
    plugin = wc.WorldClockPlugin(MANIFEST)
    plugin.config = dict(config)
    if board:
        plugin._board_tls.current = BoardContext.from_device_type(board)
    return plugin


def test_manifest_dropdowns():
    props = MANIFEST["settings_schema"]["properties"]
    for i in range(1, 7):
        assert "Europe/Amsterdam" in props[f"timezone_{i}"]["enum"]
        assert "" in props[f"timezone_{i}"]["enum"]
    assert props["time_format"]["enum"] == ["12h", "24h"]


@pytest.mark.parametrize("value", ["Europe/Amsterdam", "CET", "UTC-8", "Pacific -8", "UTC+5:30"])
def test_resolve_valid(value):
    assert datetime.now(wc.resolve_timezone(value)) is not None


def test_resolve_offset_value():
    tz = wc.resolve_timezone("Pacific -8")
    assert datetime(2026, 1, 1, tzinfo=timezone.utc).astimezone(tz).utcoffset() == timedelta(hours=-8)


@pytest.mark.parametrize("value", ["", "Nowhere/Land", "UTC+99"])
def test_resolve_invalid(value):
    with pytest.raises(ValueError):
        wc.resolve_timezone(value)


@pytest.mark.parametrize("hour,day", [(5, False), (6, True), (17, True), (18, False), (0, False)])
def test_is_daytime(hour, day):
    assert wc.is_daytime(hour) is day


def test_format_time():
    assert wc.format_time(datetime(2026, 1, 1, 16, 15), "24h") == "16:15"
    assert wc.format_time(datetime(2026, 1, 1, 4, 5), "24h") == "04:05"
    assert wc.format_time(datetime(2026, 1, 1, 16, 15), "12h") == " 4:15 PM"
    assert wc.format_time(datetime(2026, 1, 1, 0, 15), "12h") == "12:15 AM"
    assert wc.format_time(datetime(2026, 1, 1, 12, 15), "12h") == "12:15 PM"


@pytest.mark.parametrize("fmt", ["12h", "24h"])
def test_colons_aligned(fmt):
    lines = [
        wc.render_line("Home", wc.format_time(datetime(2026, 1, 1, 12, 15), fmt), True, 22),
        wc.render_line("Papa", wc.format_time(datetime(2026, 1, 1, 4, 15), fmt), False, 22),
    ]
    assert lines[0].index(":") == lines[1].index(":")


def test_render_line_tile_at_end_and_truncation():
    day = wc.render_line("A very long name indeed", "12:15", True, 22)
    night = wc.render_line("Papa", "04:15", False, 22)
    assert day.endswith("12:15{yellow}")
    assert night.endswith("04:15{black}")
    assert len(day.replace("{yellow}", "X")) == 22
    assert day.startswith("A VERY LONG NAM ")


def test_validate_config():
    plugin = make(CONFIG)
    assert plugin.validate_config(CONFIG) == []
    assert plugin.validate_config({}) 
    assert plugin.validate_config({**CONFIG, "timezone_1": "Bogus/Zone"})
    assert plugin.validate_config({**CONFIG, "name_1": ""})
    assert plugin.validate_config({**CONFIG, "timezone_1": ""})
    assert plugin.validate_config({**CONFIG, "time_format": "13h"})
    two = {k: v for k, v in CONFIG.items() if not k.endswith("_3")}
    assert plugin.validate_config(two)


def test_fetch_data_flagship_and_note():
    cfg = {**CONFIG, "name_4": "Four", "timezone_4": "UTC", "name_5": "Five", "timezone_5": "UTC"}
    result = make(cfg, "flagship").fetch_data()
    assert result.available and len(result.formatted_lines) == 5
    assert all(line.endswith(("{yellow}", "{black}")) for line in result.formatted_lines)
    note = make(cfg, "note").fetch_data()
    assert len(note.formatted_lines) == 3
    assert result.data["world_clock"] == "\n".join(result.formatted_lines)


def test_fetch_data_default_board_and_formatted_display():
    plugin = make(CONFIG)
    assert len(plugin.get_formatted_display()) == 3


def test_fetch_data_error():
    result = make({**CONFIG, "timezone_1": "Bogus/Zone"}).fetch_data()
    assert not result.available and result.error
    assert make({**CONFIG, "timezone_1": "Bogus/Zone"}).get_formatted_display() is None
