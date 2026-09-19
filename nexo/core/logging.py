"""Minimal logging configuration for the NEXO core.

This module intentionally provides a minimal, non-invasive
configuration so we don't immediately replace the project's
existing file-based logging behavior. It's safe to expand later.
"""

import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


__all__ = ["configure_logging"]
