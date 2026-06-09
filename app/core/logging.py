import logging

from app.core.config import settings


REQUEST_LOG_FIELDS = (
    "request_id",
    "method",
    "path",
    "status_code",
    "process_time",
)


class RequestLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        for field in REQUEST_LOG_FIELDS:
            if not hasattr(record, field):
                setattr(record, field, "-")

        return super().format(record)


def configure_logging() -> None:
    formatter = RequestLogFormatter(
        "%(asctime)s %(levelname)s %(name)s "
        "request_id=%(request_id)s method=%(method)s path=%(path)s "
        "status=%(status_code)s process_time=%(process_time)s "
        "message=%(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level)

    logging.getLogger("app.requests").setLevel(settings.log_level)
