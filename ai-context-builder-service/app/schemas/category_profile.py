"""Category profile."""
from pydantic import BaseModel


class CategoryProfile(BaseModel):
    category_id: str
    name: str = ""
