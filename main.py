from fastapi import FastAPI, Depends, HTTPException
import models, schemas
from database import get_db
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from sqlalchemy import text
from fastapi.responses import FileResponse


with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS todo_table"))
    conn.commit()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешает запросы со всех адресов
    allow_credentials=True,
    allow_methods=["*"], # Разрешает все методы (GET, POST и т.д.)
    allow_headers=["*"], # Разрешает все заголовки
)

@app.get("/")
async def read_index():
    return FileResponse("index.html")


@app.get("/tasks")
def get_tasks(db = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db = Depends(get_db)):
    new_task = models.Task(name=task.name)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "success"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task :schemas.TaskCreate, db = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # db_task.name = task.name
    # db_task.is_completed = task.is_completed

    update_data = task.model_dump()

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task



