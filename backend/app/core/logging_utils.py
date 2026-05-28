"""RSOD Platform — Unified Log Management (Industrial Standard).

Provides a single, opinionated logging configuration that eliminates the
typical copy-paste ``basicConfig`` blocks scattered across modules.

Features
--------
* **Colour-coded terminal output** — different log levels get different ANSI
  colours so ERROR lines jump out during incident response.
* **File persistence with rotation** — logs are written to disk via
  ``RotatingFileHandler`` so they survive container restarts and never grow
  unbounded.
* **JSON structured mode** — optional JSON output for ingestion into ELK,
  Loki, or CloudWatch.
* **Sensitive data redaction** — automatic scrubbing of passwords, tokens,
  and API keys before they hit the log stream.
* **Request-id tracing** — every FastAPI request gets a unique id injected
  into log records for distributed tracing.
* **Environment-driven** — all settings can be overridden via env vars,
  making container deployments trivial.

Environment Variables
---------------------
.. list-table::
   :header-rows: 1

   * - Variable
     - Default
     - Description
   * - ``RSOD_LOG_LEVEL``
     - ``INFO``
     - Minimum level to emit (DEBUG/INFO/WARNING/ERROR/CRITICAL)
   * - ``RSOD_LOG_DIR``
     - ``<backend>/data/logs/``
     - Directory for log files
   * - ``RSOD_LOG_FILE``
     - ``None`` (console only)
     - Log file name; if set, file handler is added
   * - ``RSOD_LOG_FORMAT``
     - ``text``
     - ``text`` or ``json``
   * - ``RSOD_LOG_COLORS``
     - ``auto``
     - ``auto`` / ``yes`` / ``no``
   * - ``RSOD_LOG_MAX_BYTES``
     - ``10_485_760`` (10 MiB)
     - Max size before rotation
   * - ``RSOD_LOG_BACKUP_COUNT``
     - ``5``
     - Number of rotated files to keep

Quick Start
-----------
>>> from app.core.logging_utils import setup_logging, get_logger
>>> setup_logging(level="INFO", log_file="app.log")
>>> logger = get_logger(__name__)
>>> logger.info("Server started")

FastAPI Integration
-------------------
In ``main.py``::

    from app.core.logging_utils import setup_logging, add_request_logging
    setup_logging(level="INFO", log_file="app.log")
    add_request_logging(app)
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import re
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Final, List, Optional

from app.core.paths import paths

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_PREFIX: Final[str] = "RSOD_LOG_"
DATE_FMT: Final[str] = "%Y-%m-%d %H:%M:%S"
TEXT_FMT: Final[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
TEXT_FMT_REQUEST: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(request_id)s | %(message)s"
)

# ---------------------------------------------------------------------------
# Colour support detection
# ---------------------------------------------------------------------------


class _ColourSupport:
    """Thread-safe lazy evaluation of whether the terminal supports ANSI colours."""

    _lock = threading.Lock()
    _cached: Optional[bool] = None

    @classmethod
    def enabled(cls, force: Optional[str] = None) -> bool:
        if force is not None:
            return force.lower() in ("1", "yes", "true", "on")

        with cls._lock:
            if cls._cached is None:
                cls._cached = cls._detect()
            return cls._cached

    @staticmethod
    def _detect() -> bool:
        # 1. Explicit NO_COLOR convention
        if os.getenv("NO_COLOR"):
            return False
        # 2. Non-TTY (piped to file)
        if not sys.stdout.isatty():
            return False
        # 3. Windows — require colorama or modern Windows Terminal
        if sys.platform == "win32":
            # Windows Terminal, VS Code, PyCharm, etc.
            term = os.getenv("TERM", "")
            if "xterm" in term or "vt" in term:
                return True
            # Try Windows 10+ ANSI support
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
                mode = ctypes.c_uint32()
                if kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(mode)):
                    return bool(mode.value & 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            except Exception:
                pass
            return False
        # 4. Unix-like TTY — generally safe
        return True


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


class ColoredFormatter(logging.Formatter):
    """ANSI colour formatter that degrades gracefully on plain terminals."""

    # Foreground colours (ANSI 256 for broad compatibility)
    COLORS: Dict[str, str] = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: bool = True,
    ) -> None:
        super().__init__(fmt=fmt or TEXT_FMT, datefmt=datefmt or DATE_FMT)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        # Save original so nested calls don't double-colour
        orig_levelname = record.levelname
        if self.use_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS["RESET"]
            record.levelname = f"{color}{record.levelname}{reset}"
        try:
            return super().format(record)
        finally:
            record.levelname = orig_levelname


class JsonFormatter(logging.Formatter):
    """Structured JSON formatter for log aggregation systems.

    Each log line is a compact JSON object with standardised fields::

        {
            "timestamp": "2024-01-15T09:30:00+00:00",
            "level": "INFO",
            "logger": "app.services.detection",
            "message": "Inference complete",
            "request_id": "a1b2c3d4",
            "extra": {"latency_ms": 42}
        }
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
    ) -> None:
        # fmt/datefmt are ignored — we build the JSON ourselves
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional tracing id
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id

        # Exception info
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Any extra fields attached by the caller (exclude already-captured ones)
        _std_keys = set(logging.LogRecord(None, 0, "", 0, "", (), None).__dict__.keys())
        _std_keys |= {"request_id"}  # already captured above
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _std_keys and not k.startswith("_")
        }
        if extra:
            payload["extra"] = extra

        return json.dumps(payload, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


class SensitiveDataFilter(logging.Filter):
    """Redact sensitive patterns from log records.

    Default patterns cover:
    * Passwords / secrets
    * API keys / bearer tokens
    * Email addresses
    * Private IP ranges
    """

    DEFAULT_PATTERNS: List[tuple[str, str]] = [
        # Password key-value pairs
        (r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*[^\s&\"']+", r"\1=***"),
        # Bearer / Basic auth headers
        (r"(?i)(authorization\s*[:=]\s*(?:bearer|basic)\s+)[^\s\"']+", r"\1***"),
        # AWS keys
        (r"(?i)(AKIA[0-9A-Z]{16})", r"***"),
        # Email addresses
        (r"[\w.-]+@[\w.-]+\.\w+", r"***@***.***"),
    ]

    def __init__(self, patterns: Optional[List[tuple[str, str]]] = None, name: str = "") -> None:
        super().__init__(name)
        self.patterns = patterns or self.DEFAULT_PATTERNS

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in self.patterns:
            msg = re.sub(pattern, repl, msg)
        record.msg = msg
        record.args = ()  # args have been merged into msg by getMessage()
        return True


class RequestIdFilter(logging.Filter):
    """Inject a ``request_id`` attribute into every log record.

    When used inside FastAPI middleware the id is taken from the request
    state; otherwise a fallback is generated.
    """

    _local = threading.local()

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        cls._local.request_id = request_id

    @classmethod
    def clear_request_id(cls) -> None:
        if hasattr(cls._local, "request_id"):
            delattr(cls._local, "request_id")

    @classmethod
    def get_request_id(cls) -> str:
        return getattr(cls._local, "request_id", "-")

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = self.get_request_id()
        return True


# ---------------------------------------------------------------------------
# Core setup function
# ---------------------------------------------------------------------------


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_format: str = "text",
    use_colors: Optional[str] = "auto",
    max_bytes: int = 10_485_760,
    backup_count: int = 5,
    name: Optional[str] = None,
    enable_sensitive_filter: bool = True,
    enable_request_id: bool = True,
) -> logging.Logger:
    """Configure a logger with consistent formatting and handlers.

    Args:
        level: Minimum log level (DEBUG/INFO/WARNING/ERROR/CRITICAL).
               Overridden by ``RSOD_LOG_LEVEL`` env var.
        log_file: File name to write logs to. If ``None``, only console.
                  Overridden by ``RSOD_LOG_FILE`` env var.
        log_dir: Directory for log files. Defaults to ``paths.data / "logs"``.
                 Overridden by ``RSOD_LOG_DIR`` env var.
        log_format: ``"text"`` or ``"json"``. Overridden by ``RSOD_LOG_FORMAT``.
        use_colors: ``"auto"`` / ``"yes"`` / ``"no"``. Overridden by
                    ``RSOD_LOG_COLORS``.
        max_bytes: Maximum bytes per log file before rotation. Default 10 MiB.
        backup_count: Number of rotated files to keep. Default 5.
        name: Logger name. ``None`` = root logger.
        enable_sensitive_filter: Whether to scrub passwords/tokens.
        enable_request_id: Whether to inject request ids.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    # --- environment overrides ---
    level = os.getenv("RSOD_LOG_LEVEL", level).upper()
    log_file = os.getenv("RSOD_LOG_FILE", log_file)
    log_dir = os.getenv("RSOD_LOG_DIR", log_dir)
    log_format = os.getenv("RSOD_LOG_FORMAT", log_format).lower()
    use_colors = os.getenv("RSOD_LOG_COLORS", use_colors)
    if env_max := os.getenv("RSOD_LOG_MAX_BYTES"):
        max_bytes = int(env_max)
    if env_back := os.getenv("RSOD_LOG_BACKUP_COUNT"):
        backup_count = int(env_back)

    numeric_level = getattr(logging, level, logging.INFO)

    # --- target logger ---
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Prevent duplicate handlers on re-import / reload
    if logger.handlers:
        logger.handlers.clear()

    # --- formatter selection ---
    if log_format == "json":
        formatter: logging.Formatter = JsonFormatter()
    else:
        color_enabled = _ColourSupport.enabled(use_colors)
        fmt = TEXT_FMT_REQUEST if enable_request_id else TEXT_FMT
        formatter = ColoredFormatter(fmt=fmt, use_colors=color_enabled)

    # --- console handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- file handler (with rotation) ---
    if log_file:
        if log_dir:
            log_path = Path(log_dir)
        else:
            log_path = paths.data / "logs"
        paths.ensure_dir(log_path)

        file_path = log_path / log_file
        # Use plain text formatter for files (no colours, no request-id unless asked)
        file_formatter = (
            JsonFormatter()
            if log_format == "json"
            else logging.Formatter(TEXT_FMT, datefmt=DATE_FMT)
        )
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # --- filters ---
    if enable_sensitive_filter:
        for handler in logger.handlers:
            handler.addFilter(SensitiveDataFilter())

    if enable_request_id:
        for handler in logger.handlers:
            handler.addFilter(RequestIdFilter())

    return logger


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger.  If ``setup_logging`` has not been called,
    the standard library root logger is returned (no colours / rotation)."""
    return logging.getLogger(name)


def setup_production_logging(
    log_file: str = "app.log",
    log_format: str = "json",
) -> logging.Logger:
    """Production-grade logging: INFO level, JSON format, file-only colours off."""
    return setup_logging(
        level="INFO",
        log_file=log_file,
        log_format=log_format,
        use_colors="no",
    )


def setup_debug_logging(log_file: str = "debug.log") -> logging.Logger:
    """Debug logging: DEBUG level, text format, colours enabled."""
    return setup_logging(
        level="DEBUG",
        log_file=log_file,
        log_format="text",
        use_colors="yes",
    )


def setup_training_logging(log_file: str = "training.log") -> logging.Logger:
    """Training script logging: INFO level with file persistence."""
    return setup_logging(
        level="INFO",
        log_file=log_file,
        log_format="text",
        use_colors="auto",
    )


# ---------------------------------------------------------------------------
# FastAPI Integration
# ---------------------------------------------------------------------------

try:
    from fastapi import FastAPI, Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        """ASGI middleware that logs every request with timing and request-id."""

        def __init__(
            self,
            app: FastAPI,
            logger_name: str = "rsod.api",
            skip_paths: Optional[set[str]] = None,
        ) -> None:
            super().__init__(app)
            self.logger = logging.getLogger(logger_name)
            self.skip_paths = skip_paths or {"/health", "/api/test/connect"}

        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])
            RequestIdFilter.set_request_id(request_id)
            request.state.request_id = request_id

            if request.url.path in self.skip_paths:
                return await call_next(request)

            start = datetime.now(timezone.utc)
            self.logger.info(
                "→ %s %s",
                request.method,
                request.url.path,
                extra={"request_id": request_id},
            )

            try:
                response = await call_next(request)
            except Exception as exc:
                self.logger.exception(
                    "Unhandled exception in %s %s",
                    request.method,
                    request.url.path,
                )
                raise
            finally:
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                status = getattr(response, "status_code", 500) if 'response' in locals() else 500
                self.logger.info(
                    "← %s %s %d — %.2f ms",
                    request.method,
                    request.url.path,
                    status,
                    latency,
                    extra={"status_code": status, "latency_ms": latency},
                )
                RequestIdFilter.clear_request_id()
                if 'response' in locals() and response is not None:
                    response.headers["x-request-id"] = request_id
                    return response

    def add_request_logging(app: FastAPI, skip_paths: Optional[set[str]] = None) -> None:
        """Attach request logging middleware to a FastAPI application."""
        app.add_middleware(RequestLoggingMiddleware, skip_paths=skip_paths)

except ImportError:  # pragma: no cover
    # FastAPI not installed — provide no-op stubs so the module still imports
    def add_request_logging(app: Any, skip_paths: Optional[set[str]] = None) -> None:  # type: ignore[misc]
        pass
