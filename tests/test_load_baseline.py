from perf.load_baseline import percentile, summarize


def test_percentile_returns_expected_order_statistics():
    values = [0.01, 0.02, 0.03, 0.04, 0.05]

    assert percentile(values, 0) == 0.01
    assert percentile(values, 50) == 0.03
    assert percentile(values, 100) == 0.05


def test_summarize_builds_expected_payload():
    summary = summarize(
        [0.001, 0.002, 0.003, 0.004],
        elapsed_seconds=0.5,
        target="http://api:8000/health",
    )

    assert summary["target"] == "http://api:8000/health"
    assert summary["count"] == 4
    assert summary["total_seconds"] == 0.5
    assert summary["throughput_rps"] == 8.0
    assert summary["min_ms"] == 1.0
    assert summary["max_ms"] == 4.0
    assert summary["mean_ms"] == 2.5
    assert summary["p50_ms"] == 3.0
