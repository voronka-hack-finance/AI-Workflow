"""Data quality metadata."""
from pydantic import BaseModel


class DataQuality(BaseModel):
    completeness: float = 1.0
    warnings: list[str] = []
