import logging

import sentry_sdk

from app.core.config import Settings, settings


logger = logging.getLogger("app.error_tracking")


def initialize_error_tracking(app_settings: Settings = settings) -> bool:
    if not app_settings.sentry_dsn:
        logger.info("sentry_disabled")
        return False

    sentry_sdk.init(
        dsn=app_settings.sentry_dsn,
        environment=app_settings.environment,
        traces_sample_rate=app_settings.sentry_traces_sample_rate,
        send_default_pii=app_settings.sentry_send_default_pii,
        release=app_settings.sentry_release or None,
    )
    logger.info("sentry_initialized environment=%s", app_settings.environment)

    return True
