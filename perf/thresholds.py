import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadThresholds:
    max_p95_ms: float | None = None
    max_p99_ms: float | None = None
    min_throughput_rps: float | None = None


DEFAULT_PROFILES: dict[str, LoadThresholds] = {
    "health": LoadThresholds(max_p95_ms=500.0, min_throughput_rps=10.0),
    "health-ready": LoadThresholds(max_p95_ms=2000.0, min_throughput_rps=5.0),
}

PROFILE_PATHS: dict[str, str] = {
    "health": "/health",
    "health-ready": "/health/ready",
}


def load_profiles_file(path: Path) -> dict[str, LoadThresholds]:
    raw_profiles = json.loads(path.read_text(encoding="utf-8"))
    profiles: dict[str, LoadThresholds] = {}

    for profile_name, values in raw_profiles.items():
        profiles[profile_name] = LoadThresholds(
            max_p95_ms=values.get("max_p95_ms"),
            max_p99_ms=values.get("max_p99_ms"),
            min_throughput_rps=values.get("min_throughput_rps"),
        )

    return profiles


def resolve_profile(
    profile_name: str,
    *,
    profiles_file: Path | None = None,
) -> tuple[LoadThresholds, str]:
    profiles = DEFAULT_PROFILES.copy()

    if profiles_file is not None:
        profiles.update(load_profiles_file(profiles_file))

    if profile_name not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown profile '{profile_name}'. Available: {available}")

    path = PROFILE_PATHS.get(profile_name, "/health")
    return profiles[profile_name], path


def merge_thresholds(
    base: LoadThresholds,
    *,
    max_p95_ms: float | None = None,
    max_p99_ms: float | None = None,
    min_throughput_rps: float | None = None,
) -> LoadThresholds:
    return LoadThresholds(
        max_p95_ms=max_p95_ms if max_p95_ms is not None else base.max_p95_ms,
        max_p99_ms=max_p99_ms if max_p99_ms is not None else base.max_p99_ms,
        min_throughput_rps=(
            min_throughput_rps
            if min_throughput_rps is not None
            else base.min_throughput_rps
        ),
    )


def evaluate_thresholds(summary: dict, thresholds: LoadThresholds) -> list[str]:
    violations: list[str] = []

    if thresholds.max_p95_ms is not None and summary["p95_ms"] > thresholds.max_p95_ms:
        violations.append(
            f"p95_ms {summary['p95_ms']} exceeds max {thresholds.max_p95_ms}",
        )

    if thresholds.max_p99_ms is not None and summary["p99_ms"] > thresholds.max_p99_ms:
        violations.append(
            f"p99_ms {summary['p99_ms']} exceeds max {thresholds.max_p99_ms}",
        )

    if (
        thresholds.min_throughput_rps is not None
        and summary["throughput_rps"] < thresholds.min_throughput_rps
    ):
        violations.append(
            "throughput_rps "
            f"{summary['throughput_rps']} below min {thresholds.min_throughput_rps}",
        )

    return violations
