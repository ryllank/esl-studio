# Copyright (c) 2026 Ryllan J E Kraft
# SPDX-License-Identifier: MIT

try:
    from ._version import __version__
except Exception:
    __version__:str = '0.unknown'
try:
    from ._version import version
except Exception:
    version:str = __version__
try:
    from ._version import build_time
except Exception:
    build_time:str = 'unknown'
__all__ = [ "__version__", "version", "build_time" ]
