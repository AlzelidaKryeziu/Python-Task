import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict

app = FastAPI()

with open('Book2.json', 'r', encoding='utf-8-sig') as json_file:
    json_data = json.load(json_file)
   
# Define a model for the fields you want to return
class BookInfo(BaseModel):
    id: str
    title: str
    abstract: str
    authors: str
    categories: str
    update_date: str
 
# Endpoints
@app.get("/papers")
async def get_json_object() -> BookInfo:
    selected_fields = {
        "id": json_data["id"],
        "title": json_data["title"],
        "abstract": json_data["abstract"],
        "authors": json_data["authors"],
        "categories": json_data["categories"],
        "update_date": json_data["update_date"]
    }
    return selected_fields
