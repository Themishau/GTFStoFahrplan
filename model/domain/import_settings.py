"""Settings required to import a GTFS archive."""

from dataclasses import dataclass


@dataclass
class ImportSettings:
    input_path: str = ""
