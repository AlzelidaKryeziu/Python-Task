import re
from sqlalchemy import create_engine, Column, Integer, String, JSON, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import json

# Define SQLAlchemy models
Base = declarative_base()

# association table for authors and papers
authors_papers = Table(
    'authors_papers',
    Base.metadata,
    Column('author_id', Integer, ForeignKey('authors.id')),
    Column('paper_id', String(), ForeignKey('papers.id'))
)


# association table for categories and papers
categories_papers = Table(
    'categories_papers',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('paper_id', String(), ForeignKey('papers.id'))
)

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(String(), primary_key=True)
    submitter = Column(String())
    title = Column(String())
    comments = Column(String())
    journal_ref = Column(String())
    doi = Column(String())
    report_no = Column(String())
    categories = Column(String())
    license = Column(String())
    abstract = Column(String())
    versions = Column(JSON)
    update_date = Column(String())
    authors_parsed = Column(JSON)
    
    # many-to-many relationship with 'authors'
    authors = relationship('Author', secondary=authors_papers, back_populates='papers')
    
    # many-to-many relationship with 'categories'
    categories = relationship('Category', secondary=categories_papers, back_populates='papers')

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), unique=True)

    papers = relationship('Paper', secondary=authors_papers, back_populates='authors')

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), unique=True)

    # many-to-many relationship with 'papers'
    papers = relationship('Paper', secondary=categories_papers, back_populates='categories')

DB_USERNAME = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "pythontask"

DB_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
session = Session()

# Load data from JSON
with open("arxiv-metadata-oai-snapshot.json", "r", encoding='utf-8-sig') as json_file:
    for line in json_file:
        entry = json.loads(line)
        
        with session.begin():
            Base.metadata.create_all(engine)

            authors_str = entry.get("authors", "")
            authors = [name.strip() for name in re.split(r', | and ', authors_str)]

            categories_str = entry.get("categories", "")
            categories = [category.strip() for category in categories_str.split(' ')]

            unique_author_names = set(authors)
            unique_category_names = set(categories)

            for name in unique_author_names:
                existing_author = session.query(Author).filter_by(name=name).first()
                if not existing_author:
                    author = Author(name=name)
                    session.add(author)

            for name in unique_category_names:
                existing_category = session.query(Category).filter_by(name=name).first()
                if not existing_category:
                    category = Category(name=name)
                    session.add(category)

            paper_categories = []
            for category_name in categories:
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    session.add(category)
                paper_categories.append(category)

            paper = Paper(
                id=entry.get("id"),
                submitter=entry.get("submitter"),
                title=entry.get("title"),
                comments=entry.get("comments"),
                journal_ref=entry.get("journal_ref", ""),
                doi=entry.get("doi"),
                report_no=entry.get("report_no"),
                license=entry.get("license"),
                abstract=entry.get("abstract"),
                versions=entry.get("versions"),
                update_date=entry.get("update_date"),
                authors_parsed=entry.get("authors_parsed"),
                categories=paper_categories
            )

            for author_name in authors:
                author = session.query(Author).filter_by(name=author_name).first()
                if author:
                    paper.authors.append(author)

            session.add(paper)

session.close()
engine.dispose()