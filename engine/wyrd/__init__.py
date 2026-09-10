"""Wyrd engine package.

Python 3.11+, standard library only (docs/design/27-tooling.md section 2).
"""

from __future__ import annotations

# The engine's own version, checked against a setting's declared requires_engine range
# (docs/design/24-authoring-a-setting.md, docs/design/29-evolution.md). Pre-1.0: no capability
# lock-in has been promised yet.
__version__ = "0.1.0"
