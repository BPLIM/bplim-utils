import sys
import os
from datetime import datetime
from typing import Union, TextIO
from pathlib import Path


class LogOpenedError(Exception):
    def __init__(self, lof_file):
        super().__init__(
            f"Log f'{lof_file}' currently active. Close it before creating a new one."
        )


class DualOutput:
    """
    Helper class to duplicate output to both a file and the console.

    Parameters
    ----------
    file : TextIO
        The file-like object (log file) to write to.
    stream : TextIO
        The original stream (usually sys.stdout or sys.stderr).
    is_stdout : bool, optional
        If True, this stream is stdout and we may add timestamps
        when printing. If False, this is stderr with no timestamps.
    """

    def __init__(self, file: TextIO, stream: TextIO, is_stdout: bool = True):
        self.file = file
        self.stream = stream
        self.is_stdout = is_stdout

    def write(self, message: str) -> None:
        """
        Write a message to both the console and the log file.

        If this is stdout and the message is non-empty, append a
        timestamp right after the message.
        """
        if self.is_stdout and message.strip():
            timestamp = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n"
            formatted_message = message + timestamp
        else:
            formatted_message = message

        # Write unmodified to the console
        self.stream.write(message)
        # Write to the file (with potential timestamp insertion)
        self.file.write(formatted_message)
        self.file.flush()

    def flush(self) -> None:
        """
        Flush both the console stream and the file buffer.
        """
        self.stream.flush()
        self.file.flush()


class BPLIMLogger:
    """
    A logger that redirects stdout and stderr to a file, allowing only one
    active logger at a time. This design also supports toggling the redirection
    on and off (via `on()` and `off()`) without fully closing the file.

    When you instantiate `BPLIMLogger`, it claims the "active logger" slot;
    any attempt to create another BPLIMLogger object before the previous one
    is closed (or freed) raises a LogOpenedError.

    After creating an instance:
      1. Call `init()` to open the file and start logging.
      2. Use `on()` and `off()` to resume or pause logging to the file.
      3. Call `close()` to fully close the log file and restore stdout/stderr.
    """

    _active_logger = None
    _active_logger_path = None

    def __init__(self, log_file: Union[Path, str], append: bool = False):
        """
        Prepare a logger instance with a log file path and append mode.
        Does not open or redirect output yet; call `init()` for that.

        Parameters
        ----------
        log_file : Union[Path, str]
            Path to the log file.
        append : bool, optional
            If True, opens the log file in append mode. Otherwise, overwrites.

        Raises
        ------
        LogOpenedError
            If another logger is already active and not closed.
        """
        # Check if there's already an active logger
        if (
            BPLIMLogger._active_logger is not None
            and not BPLIMLogger._active_logger._is_closed
        ):
            raise LogOpenedError(BPLIMLogger._active_logger_path)

        self._log_file = log_file
        self._append = append
        self._is_closed = True  # starts off closed; init() will open
        self._is_on = False  # only "on" once streams are redirected

        # Keep references to original I/O so we can restore them later
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._current_log = None

        # Claim the active logger slot; track which file is about to be used
        BPLIMLogger._active_logger = self
        BPLIMLogger._active_logger_path = os.path.abspath(self._log_file)

    def _build_status_message(self, action: str) -> str:
        """
        Builds a standardized multi-line message for logging "opened", "resumed",
        "paused", or "closed" states. Adjusts indentation based on the action.

        Parameters
        ----------
        action : str
            One of "opened", "resumed", "paused", or "closed" (by default).
            If it's not in the known set, defaults to indentation for "opened".

        Returns
        -------
        str
            A formatted message ready to be written to the log and console.
        """
        # Desired spaces in front of "log" for each action
        indent_map = {
            "opened": 7,
            "paused": 7,
            "closed": 7,
            "resumed": 8,
        }
        # Fallback if action is unrecognized
        base_indent = indent_map.get(action, 7)

        prefix_log = " " * base_indent
        prefix_action = " " + action  # e.g., " resumed" or " opened"

        return (
            f"\n{'-' * 130}\n"
            f"{prefix_log}log:  {os.path.abspath(self._log_file)}\n"
            f"{prefix_action} on:  {datetime.now().strftime('%d %b %Y, %H:%M:%S')}\n"
            + "-" * 130
            + "\n\n"
        )

    def _write_status(self, message: str) -> None:
        """
        Writes a status message to both the log file (if open) and the
        original stdout.

        Parameters
        ----------
        message : str
            The status message to log.
        """
        if self._current_log:
            self._current_log.write(message)
            self._current_log.flush()
        self._original_stdout.write(message)
        self._original_stdout.flush()

    def _redirect_streams(self) -> None:
        """
        Redirects sys.stdout and sys.stderr to the open log file via DualOutput.
        """
        sys.stdout = DualOutput(self._current_log, self._original_stdout, True)
        sys.stderr = DualOutput(self._current_log, self._original_stderr, False)

    def _restore_streams(self) -> None:
        """
        Restores the original sys.stdout and sys.stderr streams.
        """
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def init(self) -> None:
        """
        Opens the log file (if not already) and redirects output to it.
        Must be called exactly once before using the logger for actual logging.

        Raises
        ------
        Exception
            If the logger has already been initialized.
        """
        if not self._is_closed:
            raise Exception("BPLIMLogger: This logger has already been initialized.")

        mode = "a" if self._append else "w"
        self._current_log = open(self._log_file, mode)

        message = self._build_status_message("opened")
        self._write_status(message)

        self._redirect_streams()

        self._is_closed = False
        self._is_on = True

    def on(self) -> None:
        """
        Resumes redirection of output to the log file if it has been paused.
        """
        if self._is_on:
            print("Log file already on")
            return

        message = self._build_status_message("resumed")
        self._write_status(message)

        self._redirect_streams()
        self._is_on = True

    def off(self) -> None:
        """
        Pauses redirection of output to the log file without closing the file.
        """
        if not self._is_on:
            print("Log file already off")
            return

        message = self._build_status_message("paused")
        self._write_status(message)

        self._restore_streams()
        self._is_on = False

    def close(self) -> None:
        """
        Closes the log file fully and restores original stdout/stderr.
        Once closed, this logger can no longer be used to log output.

        If this logger is the currently active logger, frees up the slot
        so a new BPLIMLogger can be created.
        """
        if self._is_closed:
            return

        message = self._build_status_message("closed")
        self._write_status(message)

        self._current_log.close()
        self._restore_streams()

        self._is_closed = True
        self._is_on = False

        if BPLIMLogger._active_logger is self:
            BPLIMLogger._active_logger = None
            BPLIMLogger._active_logger_path = None
