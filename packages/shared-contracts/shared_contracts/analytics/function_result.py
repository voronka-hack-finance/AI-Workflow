"""FunctionResult contract."""
from pydantic import BaseModel, Field


class FunctionResult(BaseModel):
    function_name: str = ''
    # TODO: extend fields per architecture docs
