from pydantic import BaseModel

class TaskCreate(BaseModel):
    name: str
    is_completed: bool = False

    class Config:
        from_attributes = True