import json
from fastapi import FastAPI, HTTPException, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any, Union
from fastapi.responses import RedirectResponse, HTMLResponse
#from app.models.task import Book

'''templates = Jinja2Templates(directory="app/templates")'''

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
async def get_json_object(request: Request):
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
    #return templates.TemplateResponse("papers.html", {"request": request, "data": selected_fields_list, "endpoint": "papers"})



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
    #return templates.TemplateResponse("papers.html", {"request": request, "data": authors_list, "endpoint": "authors"})


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
    #return templates.TemplateResponse("papers.html", {"request": request, "data": categories_list, "endpoint": "categories"})


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
    #return templates.TemplateResponse("papers.html", {"request": request, "data": paper_to_return, "endpoint": f"papers/{id}"})

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
            #return templates.TemplateResponse("papers.html", {"request": request, "data": author_info, "endpoint": f"authors/{id}"})
    return {"message": "Author not found"}



@app.get("/categories/{id}", response_model=Dict[str, Union[str, List[Dict[str, str]]]])
async def get_category(id: str):
    for data in json_data["foo"]:
        if data["id"] == id:
            category_info = {
                "id": data["id"],
                "name": data["categories"],
                "papers": []
            }
            for paper in json_data["foo"]:
                if paper["categories"] == data["categories"]:
                    category_info["papers"].append({
                        "title": paper["title"]
                    })
            #return templates.TemplateResponse("papers.html", {"request": request, "data": category_info, "endpoint": f"categories/{id}"})
            return category_info
    return {"message": "Category not found"}