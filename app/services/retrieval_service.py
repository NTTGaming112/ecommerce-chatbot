import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
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


    def add_documents(self, chunks: list[str], metadatas: list[dict]):
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)

    def retrieve(self, query: str, k: int = 3):
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        return self.vector_store.similarity_search_with_relevance_scores(query, k=k)

# Singleton instance
retrieval_service = RetrievalService()
