import logging

from app.core.logging import RequestLogFormatter


def format_log_record(record: logging.LogRecord) -> str:
    formatter = RequestLogFormatter(
        "request_id=%(request_id)s method=%(method)s path=%(path)s "
        "status=%(status_code)s process_time=%(process_time)s "
        "message=%(message)s"
    )

    return formatter.format(record)


def test_request_log_formatter_includes_request_fields():
    record = logging.LogRecord(
        name="app.requests",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_finished",
        args=(),
        exc_info=None,
    )
    record.request_id = "request-1"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.process_time = 0.123

    formatted_log = format_log_record(record)

    assert "request_id=request-1" in formatted_log
    assert "method=GET" in formatted_log
    assert "path=/health" in formatted_log
    assert "status=200" in formatted_log
    assert "process_time=0.123" in formatted_log
    assert "message=request_finished" in formatted_log


def test_request_log_formatter_handles_missing_request_fields():
    record = logging.LogRecord(
        name="app.other",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="regular_log",
        args=(),
        exc_info=None,
    )

    formatted_log = format_log_record(record)

    assert "request_id=-" in formatted_log
    assert "method=-" in formatted_log
    assert "path=-" in formatted_log
    assert "status=-" in formatted_log
    assert "process_time=-" in formatted_log
    assert "message=regular_log" in formatted_log
