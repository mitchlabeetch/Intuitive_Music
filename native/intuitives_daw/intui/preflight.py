"""
    Preflight checks
"""
import subprocess

from intui.sgqt import QMessageBox
from intlib.hardware import rpi
from intlib.lib.translate import _
from intlib.lib.util import IS_MACOS
from intlib.log import LOG

__all__ = ['preflight']

RPI4_WARNING = """\
Detected a Raspberry Pi with suboptimal settings.  "
Please see https://github.com/intuitivesdaw/intuitives/src/linux/rpi4.md
"""

def _preflight_rpi():
    try:
        if rpi.is_rpi():
            if not rpi.gpu_mem():
                QMessageBox.warning(
                    None,
                    "Warning",
                    _(RPI4_WARNING),
                )
    except Exception as ex:
        LOG.exception(ex)

def _log_system_info():
    try:
        import distro
        LOG.info(distro.info())
    except Exception as ex:
        LOG.warning(ex)
    try:
        import platform
        LOG.info(f"Python version: {platform.python_version()}")
        LOG.info(f"Platform: {platform.platform()}")
        LOG.info(f"Machine Arch: {platform.machine()}")
    except Exception as ex:
        LOG.warning(ex)

def preflight():
    _log_system_info()
    _preflight_rpi()
