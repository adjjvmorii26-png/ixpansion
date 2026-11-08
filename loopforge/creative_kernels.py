"""Deterministic, dependency-free kernels for LOOPFORGE creative workflows.

These helpers do not call model providers, write files, or publish media.
They produce plans and classifications that callers can inspect before acting.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
from typing import Sequence


class ArtifactStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REFRESH = "REFRESH"
    FORK = "FORK"
    QUARANTINE = "QUARANTINE"
    ARCHIVE_CANDIDATE = "ARCHIVE-CANDIDATE"
    NEW_GAP = "NEW-GAP"


@dataclass(frozen=True)
class MemeSeed:
    seed: int
    format: str
    premise: str
    mutation: str
    caption_prompt: str


@dataclass(frozen=True)
class GifPlan:
    frame_count: int
    fps: float
    frame_duration_ms: int
    total_duration_ms: int
    loop_forever: bool


@dataclass(frozen=True)
class ArtifactAssessment:
    status: ArtifactStatus
    reason: str


def generate_meme_seeds(
    premise: str,
    *,
    count: int = 4,
    seed: int = 1337,
    formats: Sequence[str] = ("two-panel", "reaction", "expectation-reality", "tiny-victory"),
) -> list[MemeSeed]:
    """Create repeatable creative prompts; no model call or media generation occurs."""
    clean = " ".join(premise.split())
    if not clean:
        raise ValueError("premise must not be empty")
    if not 1 <= count <= 32:
        raise ValueError("count must be between 1 and 32")
    available = tuple(item.strip() for item in formats if item and item.strip())
    if not available:
        raise ValueError("at least one non-empty format is required")

    mutations = (
        "invert the expected outcome",
        "make the smallest detail absurdly important",
        "compress the situation into one dramatic beat",
        "turn the obstacle into the punchline",
        "use an overconfident narrator",
        "reveal a surprisingly wholesome ending",
        "treat a minor inconvenience as a boss battle",
        "make the background tell a second joke",
    )
    rng = random.Random(seed)
    result = []
    for index in range(count):
        chosen_format = available[index % len(available)]
        mutation = rng.choice(mutations)
        result.append(
            MemeSeed(
                seed=seed + index,
                format=chosen_format,
                premise=clean,
                mutation=mutation,
                caption_prompt=(
                    f"Create a {chosen_format} meme about: {clean}. "
                    f"Creative mutation: {mutation}. Keep text concise and legible."
                ),
            )
        )
    return result


def plan_gif(
    frame_count: int,
    *,
    fps: float = 15.0,
    max_duration_ms: int = 10_000,
    loop_forever: bool = True,
) -> GifPlan:
    """Validate a bounded GIF timing plan without allocating or encoding frames."""
    if frame_count < 2:
        raise ValueError("frame_count must be at least 2")
    if not 1 <= fps <= 60:
        raise ValueError("fps must be between 1 and 60")
    if max_duration_ms < 1:
        raise ValueError("max_duration_ms must be positive")
    duration = max(1, round(1000 / fps))
    total = frame_count * duration
    if total > max_duration_ms:
        raise ValueError(
            f"planned duration {total}ms exceeds limit {max_duration_ms}ms"
        )
    return GifPlan(
        frame_count=frame_count,
        fps=float(fps),
        frame_duration_ms=duration,
        total_duration_ms=total,
        loop_forever=bool(loop_forever),
    )


def loop_seam_score(
    first_signature: Sequence[float],
    last_signature: Sequence[float],
    *,
    max_channel_value: float = 255.0,
) -> float:
    """Return a simple normalized similarity score for caller-supplied frame signatures.

    Signatures can be compact color/luminance samples or perceptual descriptors.
    This is not a substitute for visual review or a full perceptual metric.
    """
    if not first_signature or len(first_signature) != len(last_signature):
        raise ValueError("frame signatures must be non-empty and equal length")
    if max_channel_value <= 0:
        raise ValueError("max_channel_value must be positive")
    if any(not isinstance(v, (int, float)) for v in (*first_signature, *last_signature)):
        raise ValueError("frame signatures must contain numeric values")
    distance = sum(abs(float(a) - float(b)) for a, b in zip(first_signature, last_signature))
    mean_distance = distance / len(first_signature)
    return max(0.0, min(1.0, 1.0 - mean_distance / max_channel_value))


def assess_artifact(
    *,
    age_days: int,
    reference_count: int,
    compatible: bool,
    provenance_known: bool = True,
    duplicate_of: str | None = None,
    stale_after_days: int = 90,
) -> ArtifactAssessment:
    """Classify an artifact; never deletes, moves, or overwrites anything."""
    if min(age_days, reference_count, stale_after_days) < 0:
        raise ValueError("age, reference count, and stale threshold must be non-negative")
    if not provenance_known:
        return ArtifactAssessment(ArtifactStatus.QUARANTINE, "provenance is unknown")
    if duplicate_of and reference_count == 0:
        return ArtifactAssessment(
            ArtifactStatus.ARCHIVE_CANDIDATE,
            f"unreferenced duplicate of {duplicate_of}; retain pending owner review",
        )
    if not compatible and reference_count:
        return ArtifactAssessment(
            ArtifactStatus.FORK,
            "referenced artifact is incompatible; preserve it and create a compatible fork",
        )
    if reference_count and age_days >= stale_after_days:
        return ArtifactAssessment(
            ArtifactStatus.REFRESH,
            "referenced artifact is stale; refresh on a branch and preserve provenance",
        )
    if reference_count:
        return ArtifactAssessment(ArtifactStatus.ACTIVE, "referenced and compatible")
    if age_days >= stale_after_days:
        return ArtifactAssessment(
            ArtifactStatus.ARCHIVE_CANDIDATE,
            "no references and past the stale threshold; archive only after approval",
        )
    return ArtifactAssessment(ArtifactStatus.ACTIVE, "recent artifact retained for discovery; no references found yet")
