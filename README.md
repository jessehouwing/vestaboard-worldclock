# World Clock Plugin

FiestaBoard plugin showing the local time in 3 to 6 places, one per row, with a
day/night tile (at the end of the row) (🟨 day 06:00-17:59, ⬛ night).

```
|Home             12:15 PM🟨|
|Papa              4:15 AM⬛|
```

## Configuration

Fill in `name_1`..`name_6` and `timezone_1`..`timezone_6` (the first three are required),
plus `time_format`: `12h` (AM/PM, default) or `24h`. Times are fixed-width so the colons align on every row.

Timezone is a dropdown of IANA zones (`Europe/Amsterdam`, `America/Los_Angeles`, ...). Leave empty for unused clocks.

Boards with 3 rows (Note) show the first 3 clocks; 6-row boards show up to 6.
Names are upper-cased and truncated to fit (board width minus time field).

## Template variables

`world_clock` – all lines as a string.
