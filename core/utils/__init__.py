from .config_loader import ConfigNode, ProjectConfig, load, load_content_plan
from .logging_utils import (
    log_error,
    log_info,
    log_success,
    send_telegram_alert,
    setup_logging,
)
from .secrets_manager import get as get_secret

# Optional import: model_router depends on external SDKs.
# We keep `core.utils` importable even in minimal environments.
try:
    from .model_router import ModelRouter, get_router, reset_router
except ModuleNotFoundError as _e:  # pragma: no cover

    class ModelRouter:  # type: ignore[no-redef]
        def __init__(self, *_args, **_kwargs):
            raise _e

    def get_router(*_args, **_kwargs):  # type: ignore[no-redef]
        raise _e

    def reset_router():  # type: ignore[no-redef]
        raise _e

__all__ = [
    "ConfigNode",
    "ProjectConfig",
    "load",
    "load_content_plan",
    "setup_logging",
    "log_error",
    "log_success",
    "log_info",
    "send_telegram_alert",
    "get_secret",
    "ModelRouter",
    "get_router",
    "reset_router",
]
