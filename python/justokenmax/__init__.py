"""justokenmax — attachment optimizer.

Convert expensive attachments (PDFs, images) into cheap context for coding
agents: PDFs become Markdown, images get downscaled + recompressed under the
model's resolution ceiling. Same information, a fraction of the tokens.
"""

from .optimize import optimize, OptimizeResult

__all__ = ["optimize", "OptimizeResult", "__version__"]
__version__ = "0.4.0"
