from sqlalchemy import Column, Integer, String, DateTime, Float
from app.utils.database import engine
from app.models import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True)
    submitter = Column(String(200))
    authors = Column(String(200))
    title = Column(String(500))
    comments = Column(String(500))
    journal_ref = Column(String(500))
    doi = Column(String())
    report_no = Column(String())
    categories = Column(String())
    license = Column(String(500))
    abstract = Column(String())
    versions =  Column(String())
    update_date = Column(String())
    authors_parsed= Column(String())