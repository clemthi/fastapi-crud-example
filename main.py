import os
from typing import Any, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Identity
from sqlalchemy.orm import Session, sessionmaker, declarative_base


app = FastAPI()


# region database & ORM
db_uri = os.getenv('DB_URI', 'postgresql://postgres:postgres@localhost:5432/postgres')
db_engine = create_engine(db_uri, pool_pre_ping=True)
Base = declarative_base()


class ArticleDb(Base):
    __tablename__ = 'article'
    id = Column('art_pk', Integer, Identity(), primary_key=True)
    name = Column('art_name', String(100), nullable=False)
    age = Column('art_age', Integer, nullable=True)


async def init_db():
    Base.metadata.create_all(db_engine)


async def get_db():
    try:
        db = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)()
        yield db
    finally:
        db.close()
# endregion


# region API contracts
class ArticleIn(BaseModel):
    name: str
    age: int

    class Config:
        orm_mode = True


class ArticleOut(ArticleIn):
    id: int
# endregion


# region API event & endpoints
@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get('/articles', response_model=List[ArticleOut])
async def get_articles(*, db: Session = Depends(get_db)) -> Any:
    return db.query(ArticleDb).all()


@app.post('/articles', response_model=ArticleOut)
async def add_article(*, db: Session = Depends(get_db), article_in: ArticleIn) -> Any:
    article = ArticleDb(**jsonable_encoder(article_in))
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@app.put('/articles/{id}', response_model=ArticleOut)
async def update_article(*, db: Session = Depends(get_db), id: int, article_in: ArticleIn) -> Any:
    article_db = db.query(ArticleDb).filter(ArticleDb.id == id).first()
    if not article_db:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = article_in.dict(exclude_unset=True)
    for field in jsonable_encoder(article_db):
        if field in update_data:
            setattr(article_db, field, update_data[field])

    db.add(article_db)
    db.commit()
    db.refresh(article_db)
    return article_db


@app.delete('/articles/{id}', response_model=ArticleOut)
async def delete_article(*, db: Session = Depends(get_db), id: int) -> Any:
    article = db.query(ArticleDb).filter(ArticleDb.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    return article
# endregion
