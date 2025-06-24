from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB
from pathlib import Path
from fastapi.responses import FileResponse
import os


app = FastAPI()
db_path = Path('data/database.json')
db_path.parent.mkdir(exist_ok=True)
db = TinyDB(db_path)

class Item(BaseModel):
    name: str
    description: str | None = None

class EditItem(BaseModel):
    old_name: str
    old_description: str | None = None
    new_name: str
    new_description: str | None = None

@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "home.html"))

@app.get("/items/")
async def read_all_items():
    try:
        items = db.all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/items/")
async def create_item(item: Item):
    try:
        item_dict = item.dict(exclude_unset=True)
        db.insert(item_dict)
        return item_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.post("/items/delete/")
async def delete_item(item: Item):
    try:
        items = db.all()
        for db_item in items:
            if db_item.get("name") == item.name and db_item.get("description") == item.description:
                db.remove(doc_ids=[db_item.doc_id])
                return {"message": "Item deleted successfully"}
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/items/edit/")
async def edit_item(edit: EditItem):
    try:
        items = db.all()
        for db_item in items:
            if db_item.get("name") == edit.old_name and db_item.get("description") == edit.old_description:
                db.update(
                    {"name": edit.new_name, "description": edit.new_description},
                    doc_ids=[db_item.doc_id]
                )
                return {"message": "Item updated successfully"}
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

