# Changelog

All notable changes to this project will be documented in this file.

The format is based on "Keep a Changelog" and this project adheres to Semantic Versioning.

## [0.1.0] - 2025-10-18
### Added
- Interactive scene dataframe creator: `src/data/create_data_frame.py`.
  - Prompts for a filename and collects rows interactively.
  - Row columns: `description` (scene name), `timestamp` (seconds), `level`, `tag`, `tag_type`.
  - Accepts timestamps as `MM:SS` or integer seconds; validates input and stores a human-readable `timestamp_mmss` column.
  - Saves output as pretty JSON to `data/<filename>.json`.
- Command-line launcher: `bin/create-scene-dataframe` (executable) for running the interactive script.
- Project script entry added to `pixi.toml` (`[tool.pixi.scripts] create-scene-dataframe = "bin/create-scene-dataframe"`) so the command is available when the project's Pixi environment is active.
- Project skeleton and dependencies defined in `pixi.toml` (numpy, pandas, plotly, matplotlib, etc.).
- Example notebooks and sample data files included under `notebooks/` and `data/` respectively.

### Notes
- This is the initial release for the project providing tools to build and persist scene-level data for visualization and analysis.
