import json
import os

from fastapi import FastAPI, Depends, HTTPException
import models, schemas
from database import get_db, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from sqlalchemy import text
from fastapi.responses import FileResponse
import asyncio
from aiokafka import AIOKafkaConsumer



with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS todo_table"))
    conn.commit()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_URL", "kafka:9092")
KAFKA_TOPIC = "calendar_events"



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешает запросы со всех адресов
    allow_credentials=True,
    allow_methods=["*"], # Разрешает все методы (GET, POST и т.д.)
    allow_headers=["*"], # Разрешает все заголовки
)


async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="todo-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            with SessionLocal() as session:
                data = json.loads(msg.value.decode("utf-8"))
                user_id = data.get("user_id", 0)
                expr = models.Task(
                    name=data.get("name", "Default name"),
                    user_id=user_id
                )
                session.add(expr)
                session.commit()
                session.refresh(expr)
    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())
@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/tasks")
async def get_tasks(db = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.post("/tasks")
async def create_task(task: schemas.TaskCreate, db = Depends(get_db)):
    new_task = models.Task(name=task.name)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "success"}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task :schemas.TaskCreate, db = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.model_dump()

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task



