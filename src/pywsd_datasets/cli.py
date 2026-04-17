"""Console-script entry points."""

from __future__ import annotations

import sys

from pywsd_datasets.scripts.build_all import main as _build_all
from pywsd_datasets.scripts.coverage_report import main as _coverage


def build_all() -> int:
    return _build_all(sys.argv[1:])


def coverage() -> int:
    return _coverage(sys.argv[1:])
