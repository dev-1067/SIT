from typing import List
from io import BytesIO

from PyPDF2 import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_pages(file_bytes: bytes) -> List[str]:
    """Extract text page-by-page so evidence citations can reference a page number."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        content = page.extract_text() or ""
        pages.append(content)
    return pages


def build_chunks(
    pages: List[str],
    brand: str,
    model: str,
    year: str,
    manual_id: str,
    filename: str,
) -> List[Document]:
    """Split each page into overlapping chunks, tagging every chunk with its
    source page number and vehicle metadata so retrieved evidence can be
    traced back to an exact page of an exact manual."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len)
    documents: List[Document] = []
    for page_number, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        for chunk in splitter.split_text(page_text):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "brand": brand,
                        "model": model,
                        "year": str(year),
                        "page": page_number,
                        "manual_id": manual_id,
                        "source": filename,
                    },
                )
            )
    return documents
