import gzip
import logging
import os
import sys
import traceback

from logging.handlers import RotatingFileHandler

from intlib.constants import LOG_DIR, USER_HOME

__all__ = [
    'LOG',
]

LOG = logging.getLogger(__name__)
FORMAT = (
    '[%(asctime)s] %(levelname)s %(pathname)-30s: %(lineno)s - %(message)s'
)
SG_DEBUG = 'SG_DEBUG' in os.environ


class RedactingFilter(logging.Filter):
    """
    PURPOSE: Prevents sensitive user information (like home directory paths) from appearing in log files.
    ACTION: Scans log messages and metadata for specific patterns and replaces them with generic placeholders (e.g., '~').
    MECHANISM: Overrides the filter() method to intercept log records and applies substring replacement via the redact() helper.
    """
    def __init__(self, patterns: dict):
        super(RedactingFilter, self).__init__()
        self._patterns = patterns

    def filter(self, record):
        record.msg = self.redact(record.msg)
        record.pathname = self.redact(record.pathname)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self.redact(record.args[k])
        else:
            record.args = tuple(self.redact(arg) for arg in record.args)
        return True

    def redact(self, msg):
        msg = isinstance(msg, str) and msg or str(msg)
        for k, v in self._patterns.items():
            msg = msg.replace(k, v)
        return msg

def namer(name):
    """Appends .gz extension to rotated log files."""
    return f"{name}.gz"


def rotator(source, dest):
    """
    PURPOSE: Compresses inactive log files to save disk space.
    ACTION: Compresses the source log file using GZIP and writes it to the destination.
    MECHANISM: Reads the file in binary mode, uses gzip.compress() at maximum compression level (9), and deletes the original source file.
    """
    with open(source, "rb") as sf:
        data = sf.read()
        compressed = gzip.compress(data, 9)
        with open(dest, "wb") as df:
            df.write(compressed)
    os.remove(source)

class FailProofEmitter:
    """
    PURPOSE: Ensures that logging itself does not crash the application due to encoding or IO errors.
    ACTION: Wraps the emit() call in a try-except block and fallbacks to a safe encoding.
    MECHANISM: Attempts to encode record data as 'cp850' (common on Windows) with replacements, ensuring data is always writable to the stream.
    """
    def emit(self, record):
        try:
            record = record.encode('cp850', errors='replace')
            super().emit(record)
        except Exception as ex:
            super().emit(f'FailProofEmitter: Failed to emit {record}: {ex}')

class StreamHandler(logging.StreamHandler, FailProofEmitter):
    pass

class _RotatingFileHandler(RotatingFileHandler, FailProofEmitter):
    pass

def setup_logging(
    format=FORMAT,
    level=logging.DEBUG if SG_DEBUG else logging.INFO,
    log=LOG,
    stream=sys.stdout,
    maxBytes=1024*1024*10,
):
    """
    PURPOSE: Global initialization of the application's logging infrastructure.
    ACTION: Configures both console (stdout) and file-based (rotating) log handlers.
    MECHANISM: 
        1. Creates a shared Formatter.
        2. Attaches a StreamHandler for live console feedback.
        3. Attaches a RedactingFilter to sanitize output.
        4. Attaches a _RotatingFileHandler with automatic GZIP compression.
        5. Registers a custom sys.excepthook to log uncaught exceptions.
    """
    fmt = logging.Formatter(format)
    handler = StreamHandler(
        stream=stream,
    )
    handler.setFormatter(fmt)
    log.addFilter(
        RedactingFilter({
            USER_HOME.replace('\\', '/'): "~",
            USER_HOME.replace('/', '\\'): "~",
        })
    )
    log.addHandler(handler)

    handler = _RotatingFileHandler(
        os.path.join(LOG_DIR, 'intuitives.log'),
        maxBytes=maxBytes,
        backupCount=3,
    )
    handler.setFormatter(fmt)
    handler.rotator = rotator
    handler.namer = namer
    log.addHandler(handler)

    log.setLevel(level)

    sys.excepthook = _excepthook


def _excepthook(exc_type, exc_value, tb):
    """
    PURPOSE: Captures and logs application-level crashes that aren't handled by try-except blocks.
    ACTION: Formats the exception traceback and sends it to the LOG.error channel.
    MECHANISM: Uses traceback.format_exception to convert the error data into a string and invokes LOG.error().
    """
    exc = traceback.format_exception(exc_type, exc_value, tb)
    LOG.error("\n".join(exc))

