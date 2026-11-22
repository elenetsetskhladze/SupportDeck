from fastapi import APIRouter, Depends, HTTPException
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents import vector_store
from backend.database import get_db
from backend.models.user import User
from backend.models.kb_article import KBArticle
from backend.schemas.kb import KBArticleCreate, KBArticleUpdate, KBArticleResponse, KBSearchRequest, KBSearchResult
from backend.security import require_admin, require_agent

router = APIRouter(prefix="/kb", tags=["KB"])

splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)

async def delete_chunks(article_id: int, db: AsyncSession):
    await vector_store.acreate_collection()

    await db.execute(
        text("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'article_id' = :article_id"),
        {"article_id": str(article_id)}
    )
    await db.commit()


async def index_article(article: KBArticle, db: AsyncSession):
    await delete_chunks(article.id, db)

    if not article.is_published:
        return

    chunks = splitter.split_text(article.content)

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "article_id": article.id,
                "title": article.title,
                "category": article.category
            }
        )
        for chunk in chunks
    ]

    await vector_store.aadd_documents(documents)

@router.post("/articles", response_model=KBArticleResponse, status_code=201)
async def create_kb_article(
        article: KBArticleCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_admin)
):
    new_article = KBArticle(**article.model_dump())

    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)

    await index_article(new_article, db)

    return new_article

@router.get("/articles", response_model=list[KBArticleResponse])
async def get_kb_articles(
        current_user: User = Depends(require_agent),
        db: AsyncSession = Depends(get_db)
):
    results = await db.scalars(select(KBArticle).order_by(KBArticle.id))

    return results.all()

@router.put("/articles/{article_id}", response_model=KBArticleResponse)
async def update_kb_article(
        article_id: int,
        article: KBArticleUpdate,
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    db_article = await db.get(KBArticle, article_id)

    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    for field, value in article.model_dump(exclude_unset=True).items():
        setattr(db_article, field, value)

    await db.commit()
    await db.refresh(db_article)

    await index_article(db_article, db)
    return db_article

@router.delete("/articles/{article_id}", status_code=204)
async def delete_kb_article(
        article_id: int,
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    db_article = await db.get(KBArticle, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(db_article)
    await db.commit()

    await delete_chunks(article_id, db)

@router.post("/search", response_model=list[KBSearchResult])
async def search_kb(
        search: KBSearchRequest,
        current_user: User = Depends(require_agent)
):
    results = await vector_store.asimilarity_search_with_relevance_scores(search.query, k=4)

    return [
        {
            "article_id": document.metadata["article_id"],
            "title": document.metadata["title"],
            "content": document.page_content,
            "score": score
        }
        for document, score in results
    ]