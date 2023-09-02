from fastapi import FastAPI, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncpg
from asyncpg import Connection

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/pythontask"

async def get_db_conn() -> Connection:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

class PaperModel:
    def __init__(self, id, submitter, title, comments, journal_ref, doi, report_no, license, abstract, versions, update_date, authors_parsed, categories):
        self.id = id
        self.submitter = submitter
        self.title = title
        self.comments = comments
        self.journal_ref = journal_ref
        self.doi = doi
        self.report_no = report_no
        self.license = license
        self.abstract = (abstract[:80] + '...') if len(abstract) > 80 else abstract
        self.versions = str(versions).replace('{', '').replace('[', '').replace('"', '').replace('{', '').replace(']', '')
        self.update_date = update_date
        self.authors_parsed = str(authors_parsed).replace('{', '').replace('[', '').replace('"', '').replace('{', '').replace(']', '').replace(' , ', '')

        # Check if categories is string or  list
        if isinstance(categories, str):
            self.categories = categories
        else:
            self.categories = ', '.join([category.name for category in categories])

class FullPaperModel:
    def __init__(self, id, submitter, title, comments, journal_ref, doi, report_no, license, abstract, versions, update_date, authors_parsed, categories):
        self.id = id
        self.submitter = submitter
        self.title = title
        self.comments = comments
        self.journal_ref = journal_ref
        self.doi = doi
        self.report_no = report_no
        self.license = license
        self.abstract = abstract
        self.versions = str(versions).replace('{', '').replace('[', '').replace('"', '').replace('{', '').replace(']', '')
        self.update_date = update_date
        self.authors_parsed = str(authors_parsed).replace('{', '').replace('[', '').replace('"', '').replace('{', '').replace(']', '').replace(' , ', '')

        # Check if categories is a string or list
        if isinstance(categories, str):
            self.categories = categories
        else:
            self.categories = ', '.join([category.name for category in categories])

@app.get("/papers", response_class=HTMLResponse)
async def get_papers(request: Request, conn: Connection = Depends(get_db_conn)):
    try:
        query = """
            SELECT *,
                (
                    SELECT string_agg(categories.name, ', ' ORDER BY categories.name)
                    FROM categories_papers
                    JOIN categories ON categories_papers.category_id = categories.id
                    WHERE categories_papers.paper_id = papers.id
                ) AS categories
            FROM papers
        """

        
        result = await conn.fetch(query)

        papers = [PaperModel(**record) for record in result]

        return templates.TemplateResponse("papers.html", {"request": request, "papers": papers})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)

@app.get("/papers/{id}", response_class=HTMLResponse)
async def get_paper_by_id(request: Request, id: str = Path(...), conn: Connection = Depends(get_db_conn)):
    try:
        query = """
            SELECT *,
                (
                    SELECT string_agg(categories.name, ', ' ORDER BY categories.name)
                    FROM categories_papers
                    JOIN categories ON categories_papers.category_id = categories.id
                    WHERE categories_papers.paper_id = papers.id
                ) AS categories
            FROM papers
            WHERE id = $1
        """
        result = await conn.fetchrow(query, id)

        if result is None:
            return HTMLResponse(content="Paper not found", status_code=404)

        paper = FullPaperModel(**result)

        return templates.TemplateResponse("paper_id.html", {"request": request, "paper": paper})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)
