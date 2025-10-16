"""
College Football Prediction Model (cfbmodel) package.

This package provides tools for building, preprocessing, and fetching data for
college football prediction models.

Primary exports:
- CFBModel: Core class for constructing and training prediction models.
- CFBPreprocessor: Utility for preparing and transforming raw data for modeling.
- CFBDataFetcher: Component for retrieving and managing college football datasets.

Import these classes to build, preprocess, and evaluate college football prediction models.
"""
from __future__ import annotations

import os
import sys

__version__ = "2.0.0"
__author__ = "Zach Ring"

# The package can be imported either as an installed dependency (when
# ``cfbmodel`` is on ``sys.path``) or directly from a cloned repository.
# In the latter case, ``pytest`` treats the repository root as a package
# because ``__init__.py`` exists at the top level.  Absolute imports such
# as ``from model import CFBModel`` therefore fail during test discovery
# since Python resolves them relative to the package rather than as
# top-level modules.  To keep both use-cases working we ensure the package
# directory itself is also available on ``sys.path`` so direct imports of
# ``model``/``preprocessor``/``data_fetcher`` succeed.

_PACKAGE_DIR = os.path.dirname(__file__)
if _PACKAGE_DIR and _PACKAGE_DIR not in sys.path:  # pragma: no cover - path fix
    sys.path.insert(0, _PACKAGE_DIR)

# With the search path adjusted, attempt relative imports first and fall back
# to absolute imports when the package is used in a flat layout (e.g. running
# a module directly).

try:  # pragma: no cover - import resolution logic
    from .model import CFBModel
    from .preprocessor import CFBPreprocessor
    from .data_fetcher import CFBDataFetcher
except ImportError:  # pragma: no cover
    raise

__all__ = ['CFBModel', 'CFBPreprocessor', 'CFBDataFetcher']
