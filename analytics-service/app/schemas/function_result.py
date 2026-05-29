"""Single function result."""
from pydantic import BaseModel


class FunctionResult(BaseModel):
    function_name: str
    data: dict = {}
