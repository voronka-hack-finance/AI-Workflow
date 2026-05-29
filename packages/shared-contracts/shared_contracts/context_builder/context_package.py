"""ContextPackage contract."""
from pydantic import BaseModel, Field


class ContextPackage(BaseModel):
    user_id: str = ''
    # TODO: extend fields per architecture docs
