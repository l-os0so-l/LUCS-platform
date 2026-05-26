"""RSOD Platform — Centralized Path Management (Industrial Standard).

This module provides a single source of truth for all filesystem paths used
throughout the backend application.  It solves three common engineering
problems:

1. **Hard-coded paths** — paths are resolved relative to the project root
   discovered at runtime, so the app works no matter where it is cloned or
   which directory it is launched from.
2. **String-based path manipulation** — every path is a ``pathlib.Path``
   object, eliminating cross-platform ``os.path.join`` bugs.
3. **Scattered path definitions** — every directory is defined in one place,
   making refactors safe and reviews easy.

Environment Variable Overrides
------------------------------
All paths can be overridden at runtime via environment variables.  This is
required for containerised deployments (Docker / Kubernetes) where persistent
storage is mounted at arbitrary locations.

.. list-table::
   :header-rows: 1

   * - Variable
     - Default (relative to backend/)
   * - ``RSOD_ROOT``
     - Auto-detected via ``.rsod_platform`` marker
   * - ``RSOD_DATA_DIR``
     - ``<root>/backend/data/``
   * - ``RSOD_MODEL_DIR``
     - ``<root>/backend/models/``
   * - ``RSOD_STATIC_DIR``
     - ``<root>/backend/static/``
   * - ``RSOD_UPLOAD_DIR``
     - ``<root>/backend/static/uploads/``
   * - ``RSOD_RESULT_DIR``
     - ``<root>/backend/static/results/``

Example
-------
>>> from app.core.paths import paths
>>> paths.root
PosixPath('/home/user/rsod-web-platform')
>>> paths.uploads
PosixPath('/home/user/rsod-web-platform/backend/static/uploads')
>>> paths.ensure_dir(paths.uploads)
PosixPath('/home/user/rsod-web-platform/backend/static/uploads')
"""

from __future__ import annotations

import inspect
import logging
import os
import threading
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MARKER_FILE: Final[str] = ".rsod_platform"
ENV_PREFIX: Final[str] = "RSOD_"


# ---------------------------------------------------------------------------
# Root detection
# ---------------------------------------------------------------------------

def _find_project_root(
    start_path: Path | str | None = None,
    marker: str = MARKER_FILE,
) -> Path:
    """Locate the project root by walking upward until *marker* is found.

    The search starts from the directory of the **caller's** source file when
    *start_path* is not given.  This makes the function work correctly
    regardless of the current working directory or how the script was invoked.

    Args:
        start_path: Directory to start the upward search from.
        marker: File name (or directory name) that identifies the root.

    Returns:
        Absolute ``Path`` of the directory containing *marker*.

    Raises:
        FileNotFoundError: If *marker* cannot be found in any parent directory.
    """
    if start_path is None:
        # inspect.stack()[0] is _find_project_root itself;
        # inspect.stack()[1] is the caller (usually PathManager.__init__)
        frame = inspect.stack()[1]
        start_path = Path(frame.filename).resolve().parent
    else:
        start_path = Path(start_path).resolve()

    current: Path = start_path
    for parent in [current, *current.parents]:
        if (parent / marker).exists():
            return parent

    raise FileNotFoundError(
        f"Project root marker '{marker}' not found starting from {start_path}. "
        f"Please create a '{marker}' file in the project root (rsod-web-platform/)."
    )


# ---------------------------------------------------------------------------
# PathManager
# ---------------------------------------------------------------------------

class PathManager:
    """Thread-safe, lazily-evaluated path manager.

    All properties are evaluated on first access and then cached.  The cache
    can be cleared (useful in tests) via :meth:`invalidate_cache`.
    """

    __slots__ = ("_lock", "_root", "_cache")

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._root: Path | None = None
        self._cache: dict[str, Path] = {}

    # -- internal helpers --------------------------------------------------

    def _resolve(
        self,
        key: str,
        default_factory: callable,
    ) -> Path:
        """Return a cached path, respecting environment overrides.

        The resolution order is:
        1. In-memory cache (fast path).
        2. Environment variable ``RSOD_<KEY>`` (deployment override).
        3. *default_factory* callback (project layout default).
        """
        # Fast path: already cached
        with self._lock:
            if key in self._cache:
                return self._cache[key]

        # Environment override
        env_name = f"{ENV_PREFIX}{key.upper()}"
        env_value = os.getenv(env_name)

        if env_value:
            path = Path(env_value).resolve()
            logger.debug("Path %r overridden by %s=%s", key, env_name, path)
        else:
            path = default_factory().resolve()

        # Cache and return
        with self._lock:
            self._cache[key] = path
        return path

    def _invalidate_cache(self) -> None:
        """Clear the internal cache (intended for unit tests)."""
        with self._lock:
            self._cache.clear()
            self._root = None

    # -- project root ------------------------------------------------------

    @property
    def root(self) -> Path:
        """Project root directory (where ``.rsod_platform`` lives)."""
        if self._root is None:
            env_root = os.getenv(f"{ENV_PREFIX}ROOT")
            if env_root:
                self._root = Path(env_root).resolve()
                logger.debug("Project root overridden by env: %s", self._root)
            else:
                # Pass *this* file as the starting point so detection is robust
                self._root = _find_project_root(Path(__file__).resolve().parent)
        return self._root

    # -- backend-level directories -----------------------------------------

    @property
    def backend(self) -> Path:
        """Backend source root (``<root>/backend/``)."""
        return self._resolve("backend", lambda: self.root / "backend")

    @property
    def app(self) -> Path:
        """Application package directory (``<backend>/app/``)."""
        return self._resolve("app", lambda: self.backend / "app")

    @property
    def data(self) -> Path:
        """Data directory (``<backend>/data/``).

        Override: ``RSOD_DATA_DIR``
        """
        return self._resolve("data_dir", lambda: self.backend / "data")

    @property
    def models(self) -> Path:
        """Model weights / checkpoints directory (``<backend>/models/``).

        Override: ``RSOD_MODEL_DIR``
        """
        return self._resolve("model_dir", lambda: self.backend / "models")

    @property
    def static(self) -> Path:
        """Static files served by FastAPI (``<backend>/static/``).

        Override: ``RSOD_STATIC_DIR``
        """
        return self._resolve("static_dir", lambda: self.backend / "static")

    # -- sub-directories ---------------------------------------------------

    @property
    def uploads(self) -> Path:
        """User-uploaded images (``<static>/uploads/``).

        Override: ``RSOD_UPLOAD_DIR``
        """
        return self._resolve("upload_dir", lambda: self.static / "uploads")

    @property
    def results(self) -> Path:
        """Detection result images (``<static>/results/``).

        Override: ``RSOD_RESULT_DIR``
        """
        return self._resolve("result_dir", lambda: self.static / "results")

    @property
    def logs(self) -> Path:
        """Application log files (``<data>/logs/``).

        Override: ``RSOD_LOG_DIR``
        """
        return self._resolve("log_dir", lambda: self.data / "logs")

    # -- utility methods ---------------------------------------------------

    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Ensure *path* exists as a directory, creating parents if needed.

        Returns the same ``Path`` instance so it can be used inline::

            output_file = paths.ensure_dir(paths.results) / "out.jpg"
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def init_all_dirs(self) -> None:
        """Create every known directory if it does not already exist.

        This is useful during application startup to guarantee that
        upload / result / log folders are present before the first request.
        """
        for name in (
            "data",
            "models",
            "static",
            "uploads",
            "results",
            "logs",
        ):
            self.ensure_dir(getattr(self, name))
            logger.debug("Directory ensured: %s", getattr(self, name))


# ---------------------------------------------------------------------------
# Module-level singleton — import and use directly.
# ---------------------------------------------------------------------------

paths = PathManager()
"""Global path manager instance.

Import this object and access its properties::

    from app.core.paths import paths
    model_path = paths.models / "yolo11n.pt"
"""
