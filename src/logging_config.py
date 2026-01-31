import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_ROOT_CONFIGURED = False


def configure_logging():
    """Configure the root logger with a stream handler (once).

    Per-module file handlers are managed by `get_logger()` so each
    important module gets its own file in the `logs/` directory.
    """
    global _ROOT_CONFIGURED
    if _ROOT_CONFIGURED:
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    _ROOT_CONFIGURED = True


def _sanitize_name(name: str) -> str:
    return name.replace(".", "_").replace(os.sep, "_")


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes to a per-module file in `logs/` and to stream.

    Calling this multiple times for the same `name` is safe and idempotent.
    """
    configure_logging()

    logger = logging.getLogger(name)

    # If we've already configured the file handler for this logger, return.
    if getattr(logger, "_file_handler_configured", False):
        return logger

    safe = _sanitize_name(name)
    filename = os.path.join(LOG_DIR, f"{safe}.log")
    abs_path = os.path.abspath(filename)

    # Avoid adding duplicate file handlers
    for h in logger.handlers:
        try:
            if hasattr(h, "baseFilename") and os.path.abspath(h.baseFilename) == abs_path:
                logger._file_handler_configured = True
                return logger
        except Exception:
            continue

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh = RotatingFileHandler(abs_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setLevel(logger.level or logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Allow propagation so the root stream handler still emits to console
    logger.propagate = True
    logger._file_handler_configured = True
    return logger


__all__ = ["configure_logging", "get_logger"]
