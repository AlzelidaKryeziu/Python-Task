from fastapi import FastAPI, Request, Depends, Path, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncpg
from asyncpg import Connection
from sqlalchemy import func

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
        self.abstract = (abstract[:60] + '...') if len(abstract) > 60 else abstract
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

class AuthorModel:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        # Add other attributes here if needed

        
class AuthorDetailModel:
    def __init__(self, id, name, papers):
        self.id = id
        self.name = name
        self.papers = papers

class CategoryModel:
    def __init__(self, id, name):
        self.id = id
        self.name = name

@app.get("/papers", response_class=HTMLResponse)
async def get_papers(request: Request, page: int = Query(1, description="Page number", gt=0),
                     items_per_page: int = Query(10, description="Items per page", le=50),
                     conn: Connection = Depends(get_db_conn)):
    try:
        # Calculate offset based on page and items_per_page
        offset = (page - 1) * items_per_page

        # Fetch papers with pagination
        query = f'''
            SELECT *,
            (
                SELECT string_agg(categories.name, ', ' ORDER BY categories.name)
                FROM categories_papers
                JOIN categories ON categories_papers.category_id = categories.id
                WHERE categories_papers.paper_id = papers.id
            ) AS categories
            FROM papers
            LIMIT {items_per_page}
            OFFSET {offset}
        '''
        result = await conn.fetch(query)

        papers = [PaperModel(**record) for record in result]

        # Calculate the total number of papers (you might need a separate query)
        total_papers_query = "SELECT COUNT(*) FROM papers"
        total_papers = await conn.fetchval(total_papers_query)

        # Calculate total pages
        total_pages = (total_papers + items_per_page - 1) // items_per_page

        return templates.TemplateResponse(
            "papers.html",
            {
                "request": request,
                "papers": papers,
                "page": page,
                "total_pages": total_pages,  # Pass total_pages to the template
                "items_per_page": items_per_page,
            },
        )
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

@app.get("/authors", response_class=HTMLResponse)
async def get_authors(
    request: Request,
    page: int = Query(1, description="Page number", gt=0),
    items_per_page: int = Query(10, description="Items per page", le=50),
    conn: Connection = Depends(get_db_conn)
):
    try:
        # Calculate offset based on page and items_per_page
        offset = (page - 1) * items_per_page

        # Fetch authors with pagination
        query = f"SELECT id, name FROM authors LIMIT {items_per_page} OFFSET {offset}"
        result = await conn.fetch(query)

        authors = [AuthorModel(**record) for record in result]

        # Calculate the total number of authors
        total_authors_query = "SELECT COUNT(*) FROM authors"
        total_authors = await conn.fetchval(total_authors_query)

        # Calculate the total number of pages
        total_pages = (total_authors + items_per_page - 1) // items_per_page

        # Handle cases where the page number exceeds the maximum page count
        if page > total_pages:
            page = total_pages

        return templates.TemplateResponse(
            "authors.html",
            {
                "request": request,
                "authors": authors,
                "page": page,
                "total_authors": total_authors,
                "items_per_page": items_per_page,
                "total_pages": total_pages,
            },
        )
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)


'''@app.get("/authors/{id}", response_class=HTMLResponse)
async def get_author(request: Request, id: int, conn: Connection = Depends(get_db_conn)):
    try:
        # Fetch the author's ID and name
        author_query = "SELECT id, name FROM authors WHERE id = $1"
        author_record = await conn.fetchrow(author_query, id)

        if author_record:
            authors_id, author_name = author_record

            # Fetch all papers related to the author
            papers_query = """
                SELECT *
                FROM papers
                JOIN authors_papers ON papers.id = authors_papers.paper_id
                WHERE authors_papers.author_id = $1
            """
            papers_result = await conn.fetch(papers_query, id)

            # Create an instance of AuthorModel
            author_detail = AuthorModel(id=authors_id, name=author_name)

            # Create a list of PaperModel instances
            author_papers = [PaperModel(**record) for record in papers_result]

            return templates.TemplateResponse("author_id.html", {"request": request, "author_detail": author_detail, "author_papers": author_papers})
        else:
            return HTMLResponse(content="Author not found", status_code=404)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)'''

@app.get("/categories", response_class=HTMLResponse)
async def get_categories(
    request: Request,
    page: int = Query(1, description="Page number", gt=0),
    items_per_page: int = Query(10, description="Items per page", le=50),
    conn: Connection = Depends(get_db_conn)
):
    try:
        # Calculate offset based on page and items_per_page
        offset = (page - 1) * items_per_page

        # Fetch categories with pagination
        query = f"SELECT id, name FROM categories LIMIT {items_per_page} OFFSET {offset}"
        result = await conn.fetch(query)

        categories = [CategoryModel(**record) for record in result]

        # Calculate the total number of categories (you might need a separate query)
        total_categories_query = "SELECT COUNT(*) FROM categories"
        total_categories = await conn.fetchval(total_categories_query)

        # Calculate total pages
        total_pages = (total_categories + items_per_page - 1) // items_per_page

        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "categories": categories,
                "page": page,
                "total_pages": total_pages,  # Pass total_pages to the template
                "items_per_page": items_per_page,
            },
        )
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)
    
'''@app.get("/categories/{id}", response_class=HTMLResponse)
async def get_category(request: Request, id: int, conn: Connection = Depends(get_db_conn)):
    try:
        # Fetch the category's ID and name along with associated papers
        category_query = """
            SELECT categories.id, categories.name, papers.*
            FROM categories
            JOIN categories_papers ON categories.id = categories_papers.category_id
            JOIN papers ON categories_papers.paper_id = papers.id
            WHERE categories.id = $1
        """
        result = await conn.fetch(category_query, id)

        if not result:
            return HTMLResponse(content="Category not found", status_code=404)

        # Extract category information (the first row) and paper details (remaining rows)
        category_info = {
            "id": result[0]["id"],
            "name": result[0]["name"]
        }
        papers = [PaperModel(**record) for record in result]

        return templates.TemplateResponse("category_id.html", {"request": request, "category_info": category_info, "papers": papers})
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return HTMLResponse(content=error_message, status_code=500)'''
