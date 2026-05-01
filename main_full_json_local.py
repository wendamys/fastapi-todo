import json
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

DB_FILE = "data.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return {1: {"name": "Screwdriver", "price": 10.5, "is_offer": None}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {int(k): v for k, v in data.items()}


def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(fake_db, f, indent=4, ensure_ascii=False, default=str)


fake_db = load_db()


class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Цена должна быть больше нуля")
    is_offer: Optional[bool] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Task(BaseModel):
    name: str = Field(..., max_length=1)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_time(item_id: int):
    item = fake_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    save_db()
    return item


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")

    fake_db[item_id] = item.model_dump()
    save_db()
    return {"message": "Успешно обновлено", "item": fake_db[item_id]}


@app.post("/items")
def add_item(item: Item):
    uniq_id = max(fake_db.keys(), default=0) + 1
    fake_db[uniq_id] = item.model_dump()
    save_db()
    return {"id": uniq_id, **fake_db[uniq_id]}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found (delete)")
    fake_db.pop(item_id)
    save_db()
    return {"message": "Deleted"}

@app.get("/TODO")
def read_root():
    return {"Hello":"TODO"}
