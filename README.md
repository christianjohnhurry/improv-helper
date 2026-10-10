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

## Flower chart

```
pixi run chart data/my-show.json            # writes data/my-show.html
pixi run chart data/my-show.json -o out.html
```

Or from Python:

```python
from flower import SceneTable, flower_chart

fig = flower_chart(SceneTable.load_json("data/my-show.json"))
fig.show()  # or fig.write_html("chart.html")
```

Time runs along x (MM:SS) and scene level along y. Scenes at the same level are
flat lines, transitions are bezier arcs, each level has its own pastel colour
and scene names are annotated.

## Sunburst chart

```
pixi run sunburst data/my-show.json            # writes data/my-show-sunburst.html
pixi run sunburst data/my-show.json -o out.html
```

Or from Python: `sunburst_chart(SceneTable.load_json("data/my-show.json")).show()`.

An interactive time-proportional sunburst. The show title is in the centre;
ring 1 is the Opening and each base visit in show order (labelled with its
description), and each run's scenes grow outward from the base visit that
started it. Arc angle is the whole-branch time. The end marker isn't drawn.
Single and double tags are coloured differently, with the Opening and base
scenes in grey (see the legend). Hover for name, start (MM:SS from the
Opening), own length, branch length and tag type. A stats card beside the chart
shows total time, runs, max depth, % at base, mean and longest scene, and
single/double tag counts.

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
