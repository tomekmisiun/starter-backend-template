import threading
from collections import defaultdict
from time import time


REQUEST_DURATION_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
PROCESS_START_TIME = time()

_lock = threading.Lock()
_request_counts: dict[tuple[str, str, str], int] = defaultdict(int)
_request_duration_counts: dict[tuple[str, str, str], list[int]] = defaultdict(
    lambda: [0] * len(REQUEST_DURATION_BUCKETS)
)
_request_duration_sums: dict[tuple[str, str, str], float] = defaultdict(float)


def get_route_path(scope: dict) -> str:
    route = scope.get("route")

    if route is None:
        return scope.get("path", "unknown")

    return getattr(route, "path", scope.get("path", "unknown"))


def observe_request(
    *,
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
) -> None:
    key = (method, path, str(status_code))

    with _lock:
        _request_counts[key] += 1
        _request_duration_sums[key] += duration_seconds

        for index, bucket in enumerate(REQUEST_DURATION_BUCKETS):
            if duration_seconds <= bucket:
                _request_duration_counts[key][index] += 1


def render_metrics() -> str:
    with _lock:
        request_counts = dict(_request_counts)
        duration_counts = {
            key: list(counts) for key, counts in _request_duration_counts.items()
        }
        duration_sums = dict(_request_duration_sums)

    lines = [
        "# HELP app_info Application info.",
        "# TYPE app_info gauge",
        'app_info{service="starter-backend-template"} 1',
        "# HELP process_start_time_seconds Start time of the process since unix epoch.",
        "# TYPE process_start_time_seconds gauge",
        f"process_start_time_seconds {PROCESS_START_TIME}",
        "# HELP http_requests_total Total HTTP requests.",
        "# TYPE http_requests_total counter",
    ]

    for key, count in sorted(request_counts.items()):
        lines.append(f"http_requests_total{{{_labels_for_key(key)}}} {count}")

    lines.extend(
        [
            "# HELP http_request_duration_seconds HTTP request duration in seconds.",
            "# TYPE http_request_duration_seconds histogram",
        ]
    )

    for key, bucket_counts in sorted(duration_counts.items()):
        labels = _labels_for_key(key)

        for bucket, count in zip(REQUEST_DURATION_BUCKETS, bucket_counts, strict=True):
            lines.append(
                "http_request_duration_seconds_bucket"
                f"{{{labels},le=\"{bucket}\"}} {count}"
            )

        total_count = request_counts.get(key, 0)
        lines.append(
            f"http_request_duration_seconds_bucket{{{labels},le=\"+Inf\"}} {total_count}"
        )
        lines.append(
            f"http_request_duration_seconds_sum{{{labels}}} {duration_sums.get(key, 0.0)}"
        )
        lines.append(f"http_request_duration_seconds_count{{{labels}}} {total_count}")

    return "\n".join(lines) + "\n"


def _labels_for_key(key: tuple[str, str, str]) -> str:
    method, path, status_code = key

    return (
        f'method="{_escape_label_value(method)}",'
        f'path="{_escape_label_value(path)}",'
        f'status_code="{_escape_label_value(status_code)}"'
    )


def _escape_label_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
