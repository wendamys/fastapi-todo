from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "todo_table"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)

