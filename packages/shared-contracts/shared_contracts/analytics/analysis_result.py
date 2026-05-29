"""AnalysisResult contract."""
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    status: str = 'ok'
    # TODO: extend fields per architecture docs
