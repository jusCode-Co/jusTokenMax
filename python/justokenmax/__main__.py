"""Enable `python -m justokenmax ...` (used by the Node wrapper and hooks)."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
