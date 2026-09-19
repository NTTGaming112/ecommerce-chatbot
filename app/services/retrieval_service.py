"""Retrieval Service - ChromaDB Vector Store for RAG Q&A on Knowledge Base."""
import logging
from typing import List, Dict, Any, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self._initialize()

    def _initialize(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vector_store = Chroma(
                collection_name="support_docs", 
                embedding_function=self.embeddings, 
                persist_directory=settings.CHROMA_PERSIST_DIR
            )
            logger.info("ChromaDB and Embeddings initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize RetrievalService: {e}")

    def add_documents(self, chunks: List[str], metadatas: List[dict]):
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)

    def retrieve(self, query: str, k: int = 3):
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        return self.vector_store.similarity_search_with_relevance_scores(query, k=k)

    def sync_kb_from_db(self) -> Dict[str, Any]:
        """Sync all KB articles (policies, guides, regulations, FAQ) from SQLite to ChromaDB."""
        if self.vector_store is None:
            logger.warning("Vector store is not available for sync.")
            return {"status": "skipped", "message": "Vector store not initialized", "synced_chunks": 0}

        from app.services.database import db_service
        articles = db_service.get_all_kb_articles()
        if not articles:
            return {"status": "empty", "message": "No KB articles found in database", "synced_chunks": 0}

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        all_chunks = []
        all_metadatas = []

        for art in articles:
            content = f"# {art['title']}\nCategory: {art['category']}\n\n{art['content']}"
            chunks = splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "article_id": art["article_id"],
                    "title": art["title"],
                    "category": art["category"],
                    "slug": art.get("slug", ""),
                    "chunk_index": i,
                    "source": "database_kb"
                })

        if all_chunks:
            self.vector_store.add_texts(texts=all_chunks, metadatas=all_metadatas)
            logger.info("Synced %d KB chunks from %d articles into ChromaDB.", len(all_chunks), len(articles))

        return {
            "status": "success",
            "articles_count": len(articles),
            "synced_chunks": len(all_chunks)
        }

# Singleton instance
retrieval_service = RetrievalService()
