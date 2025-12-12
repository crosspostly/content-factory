from __future__ import annotations

import datetime as _dt
import logging
import sys
from pathlib import Path
from typing import Any

from . import secrets_manager


def setup_logging(project: str, date: str | None = None, *, log_dir: str | Path = "output/logs") -> Path:
    """Configure root logging (console + file).

    Returns the path to the log file.
    """

    date_str = date or _dt.date.today().isoformat()
    safe_project = "".join(c for c in project if c.isalnum() or c in {"-", "_"}) or "project"

    log_root = Path(log_dir)
    log_root.mkdir(parents=True, exist_ok=True)

    project_dir = log_root / safe_project
    project_dir.mkdir(parents=True, exist_ok=True)

    log_file = project_dir / f"{date_str}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.getLogger(__name__).info("Logging initialized: %s", log_file)
    return log_file


def log_error(message: str, exc: BaseException | None = None) -> None:
    logger = logging.getLogger("content_factory")
    if exc is None:
        logger.error(message)
    else:
        logger.exception(message, exc_info=exc)


def log_success(message: str) -> None:
    logging.getLogger("content_factory").info(message)


def send_telegram_alert(config: Any, message: str) -> None:
    """Send a Telegram message if bot credentials are present.

    This function is best-effort and never raises.
    """

    try:
        token = secrets_manager.get("TELEGRAM_BOT_TOKEN")
        chat_id = secrets_manager.get("TELEGRAM_CHAT_ID")
    except Exception as e:
        logging.getLogger(__name__).warning("Telegram secrets not available: %s", e)
        return

    try:
        import urllib.parse
        import urllib.request

        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
        req = urllib.request.Request(
            url=f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            _ = resp.read()
    except Exception as e:
        logging.getLogger(__name__).warning("Failed to send Telegram alert: %s", e)
