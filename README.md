# improv-helper

The `flower` package for analysing the structure of improv sets.

## Scene logger

```
pixi run scenes
```

Open http://localhost:8000 (not `127.0.0.1`: YouTube embeds fail with "This
video is unavailable" when the page is served from `127.0.0.1`). The server
binds to `HOST` (default `127.0.0.1`) and `PORT` (default `8000`); change the
port if 8000 is taken, e.g. `PORT=8001 pixi run scenes` and open
http://localhost:8001. Inside a container use `HOST=0.0.0.0 pixi run scenes`
(there is no authentication, so only on a trusted network). Pick a local video file or paste a YouTube link,
then log scenes while it plays. Tables are saved as JSON in `data/`.

| Key | Action |
| --- | --- |
| `O` | Start of the opening: moves the first row (default 00:00) to the current time |
| `E` | End of the show: adds an `End` row at the current time (or moves it); the last row is the end-of-show marker |
| `N` | New scene at the current time, down one level |
| `U` | New scene up one level |
| `B` | New scene back at the base level (clears the tag) |
| `1` / `2` | Set the selected scene's tag type to single / double |

Click a row to seek the video to it. Hotkeys are disabled while typing in a
field (press Enter to finish editing). "Export CSV" saves the table and downloads it as CSV.

## Charts

```
pixi run chart data/my-show.json            # writes data/my-show.html, opens on the timeline
pixi run sunburst data/my-show.json         # writes data/my-show-sunburst.html, opens on the sunburst
pixi run site                               # every table in data/ -> data/scamps-shows.html
pixi run site --view compare               # same page, opened on the comparison (needs 2+ shows)
```

All three write one standalone HTML page (D3 loads from cdnjs; the markup is
`src/flower/templates/shows_page.html`, designed to paste into a Squarespace
Code Block). `-o out.html` sets the output; `pixi run site other-dir/` reads
another directory. From Python: `show_page(SceneTable.load_json(path), view)`
or `shows_page([show_data(t), ...])`, with `view` one of `timeline`, `sunburst`, `table`, `compare`.

The page has stat tiles (show length, runs, deepest scene, % at base, average
and longest scene, single/double tags), a Run/Tag colour switch and three views:

- **Timeline**: time along x, one row per level with the base at the bottom.
  Scenes are rounded bars joined by smooth connectors; a dot on a connector is
  a single tag, two dots a double. Labels sit above the bars and are cut to
  fit. Hover highlights the scene's whole run.
- **Sunburst**: show title and length in the centre; ring 1 is the Opening and
  each base visit, with each run's scenes growing outward as a petal. Arc angle
  is branch time. Click a petal to zoom, the centre to zoom out; hovering shows
  that scene's share of the show in the centre.
- **Scenes**: the scene table with start, length, level, tag and run.

Colours are by run (lighter with depth) or by tag, with the Opening and base
salmon. `site` shows a picker for the shows, newest first; tables that
fail validation are skipped.

With two or more shows, **Compare shows** (top of the picker) puts them side by
side. Every show is timed from its own Opening at 0:00, so a recording that
starts mid-video lines up with the rest:

- **Stats**: one row per show (date, length, scenes, runs, deepest level, % at
  base, average and longest scene, single/double tags); click a header to sort
  (newest first by default), a row to open that show.
- **Timelines**: every show stacked on one shared time axis and level scale.
- **Scene lengths**: a strip per show, one dot per scene, with the average marked.
- **Trends**: key stats over show date (firms up as more shows are logged).

## Show analysis

```python
from flower import SceneTable, analyse

a = analyse(SceneTable.load_json("data/my-show.json"))
a.stats.total_time, a.stats.base_percent, a.runs[0].scenes[0].branch_length
```

The first row is the Opening and the last row is the end-of-show marker (zero
length, not a scene; log it with `E`). A scene's length runs from its
timestamp to the next row's. Its parent is the latest earlier scene one level
up, and a run is a base visit (level 0, after the Opening) plus the scenes
that grow from it. Stats: total time, runs, max depth, % of time at base
(base visits only, Opening excluded), mean and longest scene (Opening
excluded), and single vs double tag counts. Tables with fewer than two rows,
or a scene with no parent, raise `ValidationError`.

## Development

```
pixi run test
```
