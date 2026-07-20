from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv"}


def load_pdf_document(pdf_path: Path) -> list[Document]:
    loader = PyPDFLoader(str(pdf_path))
    return loader.load()

def load_text_document(file_pat: Path)-> list[Document]:
    loader = TextLoader(
        str(file_pat),
        encoding= "utf-8"
    )
    return loader.load()

def load_csv_document(file_path: Path) -> list[Document]:
    loader = CSVLoader(
        file_path=str(file_path),
        encoding="utf-8",
    )
    return loader.load()

def load_document(file_path: Path) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf_document(file_path)
    
    if suffix in {".txt", ".md"}:
        return load_text_document(file_path)
    
    if suffix == ".csv":
        return load_csv_document(file_path)
    
    raise ValueError(f"Unsupported file extension: {suffix}")


def enrich_document_metadata(
        documents: list[Document],
        department: str,
        file_path: Path
) -> list[Document]:
    enriched_document = []

    for document in documents:
        document.metadata.update(
            {
                "department": department,
                "source_file": file_path.name,
                "source_path": str(file_path),
                "source_type": "domain_knowledge_base"
            }
        )

        enriched_document.append(document)

    return enriched_document

def iter_supported_files(folder_path: Path) -> Iterable[Path]:
    for file_path in folder_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield file_path


def load_domain_documents(
        department:str,
        folder_path: str | Path,
) ->list[Document]:
    
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    
    all_documents : list[Document] = []

    for file_path in iter_supported_files(folder):
        documents = load_document(file_path)

        enrich_documents = enrich_document_metadata(
            documents=documents,
            department=department,
            file_path=file_path,
        )

        all_documents.extend(enrich_documents)
    
    return all_documents

