"""World Clock plugin for FiestaBoard.

Shows a single named clock (add several plugin instances for more)::

    Home             12:15 PM{yellow}

A yellow tile means daytime (06:00-17:59 local), a black tile means night.
"""

import logging
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any, Dict, List

import pytz

from src.devices import BoardContext
from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

DEFAULT_BOARD = BoardContext.from_device_type("flagship")

DAY_START = 6
DAY_END = 18
_OFFSET_RE = re.compile(r"(?:^|[\s(])(?:UTC|GMT)?\s*([+-])(\d{1,2})(?::?(\d{2}))?\)?$", re.IGNORECASE)


def resolve_timezone(value: str):
    """Resolve an IANA name, abbreviation (CET) or offset (``Pacific -8``)."""
    value = (value or "").strip()
    if not value:
        raise ValueError("empty timezone")
    try:
        return pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
        pass
    match = _OFFSET_RE.search(value)
    if match:
        sign = -1 if match.group(1) == "-" else 1
        hours, minutes = int(match.group(2)), int(match.group(3) or 0)
        if hours <= 14 and minutes < 60:
            return dt_timezone(sign * timedelta(hours=hours, minutes=minutes))
    raise ValueError(f"Invalid timezone: {value}")


def is_daytime(hour: int) -> bool:
    return DAY_START <= hour < DAY_END


def format_time(now: datetime, time_format: str) -> str:
    """Fixed-width time so the colons line up on every row.

    24h: ``04:15``; 12h: `` 4:15 PM``.
    """
    if time_format == "24h":
        return now.strftime("%H:%M")
    hour = now.hour % 12 or 12
    return f"{hour:>2}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}"


def render_line(name: str, time_str: str, day: bool, cols: int) -> str:
    """One row: name left, fixed-width time, then the day/night tile at the end."""
    tile = "{yellow}" if day else "{black}"
    name_width = max(cols - len(time_str) - 2, 0)
    return f"{name.upper()[:name_width]:<{name_width}} {time_str}{tile}"


class WorldClockPlugin(PluginBase):
    """Displays the time in several timezones with a day/night indicator."""

    @property
    def plugin_id(self) -> str:
        return "vestaboard_worldclock"

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        name = str(config.get("name") or "").strip()
        tz = str(config.get("timezone") or "").strip()
        if not name:
            errors.append("A name is required.")
        if not tz:
            errors.append("A timezone is required.")
        else:
            try:
                resolve_timezone(tz)
            except ValueError:
                errors.append(f"Invalid timezone: {tz}")
        if config.get("time_format", "12h") not in ("12h", "24h"):
            errors.append("Invalid time format. Must be '12h' or '24h'.")
        return errors

    def fetch_data(self) -> PluginResult:
        try:
            board = self.board or DEFAULT_BOARD
            time_format = self.config.get("time_format", "12h")
            name = str(self.config.get("name") or "").strip()
            tz = str(self.config.get("timezone") or "").strip()
            now = datetime.now(resolve_timezone(tz))
            time_str = format_time(now, time_format)
            day = is_daytime(now.hour)
            color = "{yellow}" if day else "{black}"
            line = render_line(name, time_str, day, board.cols)
            hour = now.hour % 12 or 12 if time_format != "24h" else now.hour
            return PluginResult(
                available=True,
                data={
                    "world_clock": line,
                    "label": name,
                    "time": time_str.strip(),
                    "color": color,
                    "time_format": time_format,
                    "hour": str(hour),
                    "minute": f"{now.minute:02d}",
                    "timezone": tz,
                    "day": day,
                },
                formatted_lines=[line],
            )
        except Exception as e:
            logger.exception("Error fetching world clock data")
            return PluginResult(available=False, error=str(e))

    def get_formatted_display(self) -> "List[str] | None":
        result = self.fetch_data()
        return result.formatted_lines if result.available else None
