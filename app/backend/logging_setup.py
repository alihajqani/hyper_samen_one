"""Logging setup with Jalali (Solar Hijri) daily log files.

Each day gets its own ``YYYYMMDD.log`` file named with the Jalali date (e.g.
``14050512.log``), written next to the executable. The file rolls over at local
midnight: the handler checks the current Jalali date on each emit and reopens a
new file when the day changes.
"""

from __future__ import annotations

import logging
from pathlib import Path

import jdatetime


def jalali_log_name(when: jdatetime.datetime | None = None) -> str:
    """Return the log filename for a given moment, e.g. ``14050512.log``."""
    when = when or jdatetime.datetime.now()
    return f"{when.year:04d}{when.month:02d}{when.day:02d}.log"


def list_log_files(log_dir: Path) -> list[Path]:
    """Return Jalali-named ``*.log`` files in *log_dir*, newest first."""
    d = Path(log_dir)
    if not d.is_dir():
        return []
    files = [p for p in d.glob("*.log") if p.stem.isdigit() and len(p.stem) == 8]
    return sorted(files, key=lambda p: p.stem, reverse=True)


class JalaliDailyFileHandler(logging.Handler):
    """A file handler that writes to a Jalali-dated file, one per day.

    Unlike ``TimedRotatingFileHandler`` (which renames a single base file), this
    handler writes directly into ``<jalali-date>.log`` and switches files when the
    Jalali calendar day changes.
    """

    def __init__(self, log_dir: Path, encoding: str = "utf-8") -> None:
        super().__init__()
        self._dir = Path(log_dir)
        self._encoding = encoding
        self._current_name: str | None = None
        self._stream = None
        self._dir.mkdir(parents=True, exist_ok=True)

    def _ensure_stream(self) -> None:
        name = jalali_log_name()
        if name != self._current_name or self._stream is None:
            if self._stream is not None:
                try:
                    self._stream.close()
                finally:
                    self._stream = None
            path = self._dir / name
            self._stream = open(path, "a", encoding=self._encoding)
            self._current_name = name

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._ensure_stream()
            msg = self.format(record)
            assert self._stream is not None
            self._stream.write(msg + "\n")
            self._stream.flush()
        except Exception:  # pragma: no cover - logging must never crash the app
            self.handleError(record)

    def close(self) -> None:
        try:
            if self._stream is not None:
                self._stream.close()
                self._stream = None
        finally:
            super().close()


_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(log_dir: Path, level: str = "INFO") -> logging.Logger:
    """Configure root logging with the Jalali daily handler + console output.

    Returns the application logger. Safe to call once at startup.
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    # Avoid duplicate handlers if called twice.
    for h in list(root.handlers):
        if isinstance(h, (JalaliDailyFileHandler, logging.StreamHandler)):
            root.removeHandler(h)

    formatter = logging.Formatter(_FORMAT)

    file_handler = JalaliDailyFileHandler(log_dir)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    return logging.getLogger("hyper_samen")
