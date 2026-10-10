# improv-helper

The `flower` package for analysing the structure of improv sets.

## Scene logger

```
pixi run scenes
```

Open http://127.0.0.1:8000. The server binds to `HOST` (default `127.0.0.1`)
and `PORT` (default `8000`); inside a container use `HOST=0.0.0.0 pixi run scenes`
(there is no authentication, so only on a trusted network). Pick a local video file or paste a YouTube link,
then log scenes while it plays. Tables are saved as JSON in `data/`.

| Key | Action |
| --- | --- |
| `O` | Start of the opening: moves the first row (default 00:00) to the current time |
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

## Development

```
pixi run test
```
