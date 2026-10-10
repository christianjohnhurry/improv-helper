# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-10-10

### Added
- `flower.flower_chart(table)`: renders a scene table as a Plotly flower chart
  (time on x as MM:SS, level on y, flat lines for same-level scenes, bezier
  arcs for transitions, pastel colour per level, scene names annotated).
- `pixi run chart <table.json> [-o out.html]` CLI that writes a flower chart as HTML.
- `plotly` dependency.
- Tests for the flower chart.

## [0.2.0] - 2026-10-10

### Added
- Scene logger web app (`pixi run scenes`): FastAPI server plus a single
  HTML/JS page for logging scenes against a local video file or YouTube link.
- Hotkeys for the opening start, and for new scenes (down one, up one, back to base) and for
  single/double tags; row editing, click-to-seek, save and CSV export.
- API endpoints to list, load, save and export scene tables stored in `data/`.
- `HOST` and `PORT` environment variables for `pixi run scenes` (default
  `127.0.0.1:8000`).
- `fastapi`, `uvicorn` and `httpx` dependencies.

## [0.1.0] - 2026-10-10

### Added
- `flower` package under `src/`.
- `SceneTable` model with show metadata and scene rows (description,
  timestamp in seconds, level, tag_type).
- Validation: increasing timestamps, levels >= 0, tag_type in
  `single`/`double`/empty, empty tag_type for the base scene.
- JSON save/load, CSV export, and MM:SS <-> seconds helpers.
- `flower.__version__` as the single source of the package version.
- pytest tests.
- `linux-aarch64` and `osx-arm64` pixi platforms.

[Unreleased]: https://github.com/christianjohnhurry/improv-helper/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/christianjohnhurry/improv-helper/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/christianjohnhurry/improv-helper/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/christianjohnhurry/improv-helper/releases/tag/v0.1.0
