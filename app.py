import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any, Union

app = FastAPI()

with open('Book2.json', 'r', encoding='utf-8-sig') as json_file:
    json_data = json.load(json_file)
   

class BookInfo(BaseModel):
    id: str
    title: str
    abstract: str
    authors: str
    categories: str
    update_date: str
 
# Endpoints
@app.get("/papers", response_model=List[BookInfo])
async def get_json_object():
    selected_fields_list = []
    for paper in json_data["foo"]:
        selected_fields = {
            "id": paper["id"],
            "title": paper["title"],
            "abstract": paper["abstract"],
            "authors": paper["authors"],
            "categories": paper["categories"],
            "update_date": paper["update_date"]
        }
        selected_fields_list.append(selected_fields)
    return selected_fields_list


@app.get("/papers/{id}", response_model=BookInfo)
async def get_paper_by_id(id: str):
    paper_to_return = None
    for paper in json_data["foo"]:
        if paper["id"] == id:
            paper_to_return = paper
            break
    
    if paper_to_return is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper_to_return

@app.get("/authors", response_model=List[Dict[str, str]])
async def get_authors():
    authors_list = []
    for name in json_data["foo"]:
        authors = name["authors"]
        author_list = [author.strip() for author in authors.split(',')]
        for author in author_list:
            author_info = {
                "id": name["id"],
                "name": author
            }
            if author_info not in authors_list:
                authors_list.append(author_info)
    return authors_list


@app.get("/authors/{id}", response_model=Dict[str, Union[str, List[str]]])
async def get_author(id: str):
    for data in json_data["foo"]:
        if data["id"] == id:
            author_info = {
                "id": data["id"],
                "name": data["authors"],
                "papers": []
            }
            for paper in json_data["foo"]:
                if paper["authors"] == data["authors"]:
                    author_info["papers"].append(paper["title"])
            return author_info
    return {"message": "Author not found"}



@app.get("/categories", response_model=List[Dict[str, str]])
async def get_categories():
    categories_list = []
    for data in json_data["foo"]:
        categories = data["categories"].split()
        for category in categories:
            category_info = {
                "id": data["id"],
                "name": category
            }
            if category_info not in categories_list:
                categories_list.append(category_info)
    return categories_list


@app.get("/categories/{id}", response_model=Dict[str, Union[str, List[Dict[str, str]]]])
async def get_category(id: str):
    category_info = {}
    for data in json_data["foo"]:
        if id == data["id"]:
            category_info["id"] = data["id"]
            category_info["name"] = data["categories"]
            category_info["papers"] = []
            for paper in json_data["foo"]:
                if id == paper["id"]:
                    category_info["papers"].append({
                        "title": paper["title"]
                    })
            return category_info
    return {"message": "Category not found"} #/categories/0704.0001...