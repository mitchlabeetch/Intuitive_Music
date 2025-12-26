"""
INTUITIVES DAW - Vendor Dependencies (int_vendor)

This is the new module namespace for Intuitives DAW vendor packages.
It re-exports from sg_py_vendor for backward compatibility during migration.

This package contains third-party dependencies that are bundled with
Intuitives DAW to ensure version compatibility and easy distribution.
"""

# Re-export everything from sg_py_vendor
from sg_py_vendor import *
