"""Sound time-local exclusion under explicit open-world constraints.

Inputs are source assertions, not automatically inferred from timestamp order.
This module implements established model semantics for audit and integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Status(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class Certificate:
    kind: str
    target: str
    positive_values: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    capacity: int | None = None


@dataclass(frozen=True)
class Decision:
    status: Status
    certificate: Certificate | None


@dataclass(frozen=True)
class TimeLocalEvidence:
    """All assertions must apply at one common validity time.

    Each tuple contains (value, source_id). A capacity and a complete flag each
    require their own source. Repeated values occupy only one capacity position.
    """
    positive: tuple[tuple[str, str], ...]
    negative: tuple[tuple[str, str], ...] = ()
    capacity: int | None = None
    capacity_source: str | None = None
    complete_source: str | None = None

    @staticmethod
    def _index(items: Iterable[tuple[str, str]]) -> dict[str, tuple[str, ...]]:
        index: dict[str, set[str]] = {}
        for value, source in items:
            if not isinstance(value, str) or not value:
                raise ValueError("Every value needs a nonempty string.")
            if not isinstance(source, str) or not source:
                raise ValueError("Every assertion needs a source identifier.")
            index.setdefault(value, set()).add(source)
        return {value: tuple(sorted(sources)) for value, sources in index.items()}

    def decide(self, target: str) -> Decision:
        if not isinstance(target, str) or not target:
            raise ValueError("The target needs a nonempty string.")
        positives = self._index(self.positive)
        negatives = self._index(self.negative)
        if set(positives) & set(negatives):
            raise ValueError("The time-local positive and negative assertions conflict.")
        if self.capacity is not None:
            if isinstance(self.capacity, bool) or not isinstance(self.capacity, int) or self.capacity < 0:
                raise ValueError("Capacity must be a nonnegative integer or None.")
            if not isinstance(self.capacity_source, str) or not self.capacity_source:
                raise ValueError("Capacity requires a source assertion.")
            if len(positives) > self.capacity:
                raise ValueError("The positive assertions exceed the stated capacity.")
        if self.complete_source is not None and (
            not isinstance(self.complete_source, str) or not self.complete_source
        ):
            raise ValueError("A complete state requires a source assertion.")
        if target in positives:
            return Decision(Status.PRESENT, Certificate(
                "positive", target, (target,), (positives[target][0],)))
        if target in negatives:
            return Decision(Status.ABSENT, Certificate(
                "explicit_negative", target, source_ids=(negatives[target][0],)))
        values = tuple(sorted(positives))
        if self.complete_source is not None:
            return Decision(Status.ABSENT, Certificate(
                "complete_state", target, values,
                (self.complete_source,) + tuple(positives[value][0] for value in values)))
        if self.capacity is not None and len(positives) == self.capacity:
            return Decision(Status.ABSENT, Certificate(
                "capacity_saturation", target, values,
                (self.capacity_source,) + tuple(positives[value][0] for value in values),
                self.capacity))
        return Decision(Status.UNRESOLVED, None)
