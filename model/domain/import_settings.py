"""Settings required to import a GTFS archive."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ImportSettings:
    input_path: Path | None = None
