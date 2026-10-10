# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/christianjohnhurry/improv-helper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/christianjohnhurry/improv-helper/releases/tag/v0.1.0
