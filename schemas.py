from pydantic import BaseModel
class PropertyModel(BaseModel):
    dateofbirth: str
    position: str
    city: str