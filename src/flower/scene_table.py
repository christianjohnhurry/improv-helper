"""Scene table model: show metadata plus an ordered list of scenes."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

TAG_TYPES = frozenset({"single", "double", ""})
CSV_COLUMNS = ("description", "timestamp", "level", "tag_type")


class ValidationError(ValueError):
    """Raised when a scene table violates its invariants."""


def parse_timestamp(text: str) -> int:
    """Convert 'MM:SS' (minutes may exceed 59) to seconds."""
    minutes, sep, seconds = text.strip().partition(":")
    if not sep or not minutes.isdigit() or not seconds.isdigit():
        raise ValueError(f"invalid MM:SS timestamp: {text!r}")
    if int(seconds) > 59:
        raise ValueError(f"seconds out of range in timestamp: {text!r}")
    return int(minutes) * 60 + int(seconds)


def format_timestamp(seconds: int) -> str:
    """Convert seconds to 'MM:SS'."""
    if seconds < 0:
        raise ValueError(f"negative timestamp: {seconds}")
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


@dataclass
class ShowMetadata:
    title: str = ""
    date: str = ""
    video_source: str = ""


@dataclass
class Scene:
    description: str
    timestamp: int  # seconds
    level: int = 0
    tag_type: str = ""  # 'single' | 'double' | '' (empty when back at base scene)


@dataclass
class SceneTable:
    metadata: ShowMetadata = field(default_factory=ShowMetadata)
    scenes: list[Scene] = field(default_factory=list)

    def validate(self) -> None:
        previous = None
        for i, scene in enumerate(self.scenes):
            if scene.level < 0:
                raise ValidationError(f"scene {i}: level must be >= 0, got {scene.level}")
            if scene.tag_type not in TAG_TYPES:
                raise ValidationError(f"scene {i}: invalid tag_type {scene.tag_type!r}")
            if scene.level == 0 and scene.tag_type != "":
                raise ValidationError(
                    f"scene {i}: returning to the base scene must have an empty tag_type"
                )
            if previous is not None and scene.timestamp <= previous:
                raise ValidationError(
                    f"scene {i}: timestamp {scene.timestamp} is not after {previous}"
                )
            previous = scene.timestamp

    def to_dict(self) -> dict:
        return {
            "metadata": asdict(self.metadata),
            "scenes": [asdict(s) for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SceneTable:
        table = cls(
            metadata=ShowMetadata(**data.get("metadata", {})),
            scenes=[Scene(**s) for s in data.get("scenes", [])],
        )
        table.validate()
        return table

    def save_json(self, path: str | Path) -> None:
        self.validate()
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def load_json(cls, path: str | Path) -> SceneTable:
        return cls.from_dict(json.loads(Path(path).read_text()))

    def export_csv(self, path: str | Path) -> None:
        """Write scene rows only, with timestamps as MM:SS."""
        self.validate()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for s in self.scenes:
                writer.writerow(
                    [s.description, format_timestamp(s.timestamp), s.level, s.tag_type]
                )
