"""Normalized transaction."""
from pydantic import BaseModel


class NormalizedTransaction(BaseModel):
    id: str
    amount: float = 0.0
    # TODO: extend
