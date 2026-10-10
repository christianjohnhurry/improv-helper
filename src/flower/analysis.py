"""Structure analysis of a scene table: lengths, runs, scene tree and show stats.

Conventions: the first row is the Opening and the last row is the end-of-show
marker (zero length, not a scene). A scene runs from its timestamp to the next
row's. A run is a base visit (level 0, after the Opening) plus the scenes that
grow from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from flower.scene_table import Scene, SceneTable, ValidationError


@dataclass
class SceneNode:
    """A scene in the tree, with its own and branch lengths in seconds."""

    scene: Scene
    index: int  # row index in the table
    length: int
    parent: SceneNode | None = None
    children: list[SceneNode] = field(default_factory=list)

    @property
    def branch_length(self) -> int:
        """Own length plus the lengths of all descendants."""
        return self.length + sum(c.branch_length for c in self.children)


@dataclass
class Run:
    """A base visit and the scenes that grow from it, in show order."""

    base: SceneNode
    scenes: list[SceneNode]

    @property
    def length(self) -> int:
        return self.base.branch_length


@dataclass
class ShowStats:
    total_time: int  # seconds, Opening to end marker
    run_count: int
    max_depth: int
    base_percent: float  # % of total time spent in base visits (Opening excluded)
    mean_scene_length: float  # seconds, over scenes after the Opening
    longest_scene: SceneNode | None
    single_tags: int
    double_tags: int


@dataclass
class ShowAnalysis:
    opening: SceneNode
    runs: list[Run]
    stats: ShowStats


def scene_lengths(table: SceneTable) -> list[int]:
    """Length of each row in seconds: its timestamp to the next row's.

    Args:
        table: The scene table.

    Returns:
        One length per row; the last row (end-of-show marker) is 0.

    Raises:
        ValidationError: If the table has fewer than two rows.
    """
    scenes = table.scenes
    if len(scenes) < 2:
        raise ValidationError("a show needs at least an Opening and an end-of-show row")
    return [b.timestamp - a.timestamp for a, b in zip(scenes, scenes[1:])] + [0]


def analyse(table: SceneTable) -> ShowAnalysis:
    """Build the runs, scene tree and show stats for a table.

    A scene's parent is the latest earlier scene one level up within its run.

    Args:
        table: The scene table, with the end-of-show marker as its last row.

    Returns:
        The Opening, the runs in show order and the show stats.

    Raises:
        ValidationError: If the table has fewer than two rows, or a scene has
            no parent (it appears before any base visit, or skips a level).
    """
    table.validate()
    lengths = scene_lengths(table)
    nodes = [SceneNode(s, i, n) for i, (s, n) in enumerate(zip(table.scenes, lengths))]
    opening, scene_nodes = nodes[0], nodes[1:-1]  # nodes[-1] is the end marker

    runs: list[Run] = []
    stack: list[SceneNode] = []  # latest scene per level within the current run
    for node in scene_nodes:
        level = node.scene.level
        if level == 0:
            runs.append(Run(node, [node]))
            stack = [node]
            continue
        if level > len(stack):
            raise ValidationError(
                f"scene {node.index}: level {level} has no parent at level {level - 1}"
            )
        node.parent = stack[level - 1]
        node.parent.children.append(node)
        del stack[level:]
        stack.append(node)
        runs[-1].scenes.append(node)

    total = sum(lengths)
    base_time = sum(r.base.length for r in runs)
    tags = [n.scene.tag_type for n in scene_nodes]
    stats = ShowStats(
        total_time=total,
        run_count=len(runs),
        max_depth=max((n.scene.level for n in scene_nodes), default=0),
        base_percent=100 * base_time / total if total else 0.0,
        mean_scene_length=(
            sum(n.length for n in scene_nodes) / len(scene_nodes) if scene_nodes else 0.0
        ),
        longest_scene=max(scene_nodes, key=lambda n: n.length, default=None),
        single_tags=tags.count("single"),
        double_tags=tags.count("double"),
    )
    return ShowAnalysis(opening, runs, stats)
