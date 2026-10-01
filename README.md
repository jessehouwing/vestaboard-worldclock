# World Clock Plugin

FiestaBoard plugin showing the local time in a single place, with a day/night tile
(at the end of the row) (🟨 day 06:00-17:59, ⬛ night). Add multiple instances of the
plugin for more clocks (e.g. one for Home and one for Papa).

```
|Home             12:15 PM🟨|
```

## Configuration

- `name` – label (required)
- `timezone` – IANA zone dropdown such as `Europe/Amsterdam` (required)
- `time_format` – `12h` (AM/PM, default) or `24h`

Names are upper-cased and truncated to fit (board width minus time field).

## Template variables

Use as `{{vestaboard_worldclock.variable}}`.

| Variable | Description | Example |
|---|---|---|
| `world_clock` | Whole row: label, time and day/night tile | `HOME 12:15 PM{yellow}` |
| `label` | Clock label | `Home` |
| `time` | Current time string | `12:15 PM` |
| `color` | Day/night tile (`{yellow}` or `{black}`) | `{yellow}` |
| `time_format` | Active time format | `12h` |
| `hour` | Current hour | `12` |
| `minute` | Current minute | `15` |
