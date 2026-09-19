import io
import logging

import pymupdf  # PyMuPDF
import docx  # python-docx
from fastapi import APIRouter, HTTPException, UploadFile, File
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.schemas import DocumentInput
from app.core.config import settings
from app.services.retrieval_service import retrieval_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])


@router.post("", summary="Luồng Ingestion: Đẩy text tài liệu vào Vector DB")
async def ingest_document(doc: DocumentInput):
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(doc.text_content)
        metadatas = [{"document_id": doc.document_id, "chunk_index": i} for i in range(len(chunks))]
        retrieval_service.add_documents(chunks, metadatas)
        return {"status": "success", "message": f"Đã chia thành {len(chunks)} chunks và lưu thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", summary="Luồng Ingestion: Upload file tài liệu (PDF, DOCX, TXT)")
async def ingest_file(file: UploadFile = File(...)):
    try:
        logger.debug(f"Ingest file: vector_store initialized = {retrieval_service.vector_store is not None}")
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File vượt quá dung lượng cho phép.")

        filename = (file.filename or "upload").lower()
        extracted_text = ""

        if filename.endswith(".pdf"):
            doc = pymupdf.open(stream=content, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text() + "\n"
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
        elif filename.endswith(".txt"):
            extracted_text = content.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF, DOCX, TXT.")

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Không đọc được nội dung từ file hoặc file rỗng.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(extracted_text)

        document_id = file.filename
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        retrieval_service.add_documents(chunks, metadatas)

        return {"status": "success", "message": f"Đã xử lý file {file.filename}, chia thành {len(chunks)} chunks."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
