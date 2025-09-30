from __future__ import annotations

import gzip
import re
from pathlib import Path
from typing import Any

import ckan.plugins.toolkit as tk
from ckan.types import Context

from ckanext.tables.shared import (
    ColumnDefinition,
    ListDataSource,
    TableDefinition,
    formatters,
)

from ckanext.logs import config

LOG_ENTRY_START_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(INFO|ERROR|WARNING|WARNI|DEBUG|CRITICAL)\s+"
    r"\[([^\]]+)\]\s*(.*)"
)


class LogDataSource(ListDataSource):
    """Data source for reading log files with multi-line entries."""

    def __init__(self, n_logs: int = 10000):
        self.logs_path = Path(config.get_logs_folder() or "")
        self.logs_filename = config.get_log_file_name()
        self.n_logs = n_logs
        self.data: list[dict[str, Any]] = []
        self.filtered: list[dict[str, Any]] | None = None

        self._load_all_logs()

    def _load_all_logs(self):
        """Load all log entries from all files, newest first."""
        log_files = sorted(
            self.logs_path.glob(f"{self.logs_filename}*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        all_entries: list[dict[str, Any]] = []

        for log_file in log_files:
            lines = self._read_all_lines(log_file)
            entries = self._parse_lines(lines)
            all_entries.extend(entries)

            if len(all_entries) >= self.n_logs:
                break

        # sort by timestamp descending
        all_entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

        self.data = all_entries
        self.filtered = self.data

    def _read_all_lines(self, log_file: Path) -> list[str]:
        """Read all lines from a file (supports .gz)."""
        try:
            if log_file.suffix == ".gz":
                with gzip.open(log_file, "rt", errors="ignore") as f:
                    return f.readlines()
            else:
                with log_file.open("r", errors="ignore") as f:
                    return f.readlines()
        except Exception:  # noqa
            return []

    def _parse_lines(self, lines: list[str]) -> list[dict[str, Any]]:
        entries = []
        buffer: list[str] = []
        last_timestamp = ""

        for line in lines:
            match = LOG_ENTRY_START_RE.match(line)

            if match:
                if buffer:
                    entries.append(
                        {
                            "timestamp": last_timestamp,
                            "level": "ERROR",
                            "module": "traceback",
                            "message": "\n".join(buffer),
                        }
                    )
                    buffer = []

                # Start new normal log entry
                timestamp, level, module, message = match.groups()

                last_timestamp = timestamp
                entries.append(
                    {
                        "timestamp": timestamp,
                        "level": level,
                        "module": module,
                        "message": message,
                    }
                )
            else:
                buffer.append(line.rstrip())

        return entries


class LogsTable(TableDefinition):
    """Table definition for the logs dashboard."""

    def __init__(self):
        """Initialize the table definition."""
        super().__init__(
            name="logs",
            data_source=LogDataSource(),
            columns=[
                ColumnDefinition(field="timestamp", width=180, resizable=False),
                ColumnDefinition(field="level", width=100, resizable=False),
                ColumnDefinition(field="module", width=200),
                ColumnDefinition(
                    field="message",
                    formatters=[
                        (formatters.DialogModalFormatter, {}),
                    ],
                    tabulator_formatter="html",
                ),
            ],
        )

    @classmethod
    def check_access(cls, context: Context) -> None:
        tk.check_access("sysadmin", context)
