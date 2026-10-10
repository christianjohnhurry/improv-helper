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
    """Convert an 'MM:SS' string to seconds.

    Args:
        text: Timestamp as 'MM:SS'. Minutes may exceed 59; seconds must be 0-59.

    Returns:
        The timestamp in whole seconds.

    Raises:
        ValueError: If the text is not a valid MM:SS timestamp.
    """
    minutes, sep, seconds = text.strip().partition(":")
    if not sep or not minutes.isdigit() or not seconds.isdigit():
        raise ValueError(f"invalid MM:SS timestamp: {text!r}")
    if int(seconds) > 59:
        raise ValueError(f"seconds out of range in timestamp: {text!r}")
    return int(minutes) * 60 + int(seconds)


def format_timestamp(seconds: int) -> str:
    """Convert seconds to an 'MM:SS' string.

    Args:
        seconds: Non-negative timestamp in seconds.

    Returns:
        The timestamp formatted as zero-padded 'MM:SS'.

    Raises:
        ValueError: If seconds is negative.
    """
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
        """Check the table's invariants.

        Timestamps must be strictly increasing, levels must be >= 0, tag_type
        must be in TAG_TYPES, and a level-0 (base) scene must have an empty
        tag_type.

        Raises:
            ValidationError: If any invariant is violated.
        """
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
        """Convert the table to a JSON-serialisable dict.

        Returns:
            A dict with 'metadata' and 'scenes' keys.
        """
        return {
            "metadata": asdict(self.metadata),
            "scenes": [asdict(s) for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SceneTable:
        """Build a validated table from a dict as produced by to_dict.

        Args:
            data: Dict with optional 'metadata' and 'scenes' keys.

        Returns:
            The constructed SceneTable.

        Raises:
            ValidationError: If the resulting table is invalid.
        """
        table = cls(
            metadata=ShowMetadata(**data.get("metadata", {})),
            scenes=[Scene(**s) for s in data.get("scenes", [])],
        )
        table.validate()
        return table

    def save_json(self, path: str | Path) -> None:
        """Validate the table and write it to a JSON file.

        Args:
            path: Destination file path.

        Raises:
            ValidationError: If the table is invalid.
        """
        self.validate()
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def load_json(cls, path: str | Path) -> SceneTable:
        """Load and validate a table from a JSON file.

        Args:
            path: Path of the JSON file written by save_json.

        Returns:
            The loaded SceneTable.

        Raises:
            ValidationError: If the loaded table is invalid.
        """
        return cls.from_dict(json.loads(Path(path).read_text()))

    def export_csv(self, path: str | Path) -> None:
        """Validate the table and export the scene rows to CSV.

        Metadata is not included; timestamps are written as MM:SS.

        Args:
            path: Destination file path.

        Raises:
            ValidationError: If the table is invalid.
        """
        self.validate()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for s in self.scenes:
                writer.writerow(
                    [s.description, format_timestamp(s.timestamp), s.level, s.tag_type]
                )
