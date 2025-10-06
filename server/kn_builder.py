from pathlib import Path
from typing import List

import config
from document_processor import UnifiedDocumentLoader
from langchain_core.documents import Document
from loguru import logger
from vector_store import VLLMEmbedding, create_vector_store


def build_offline_knowledge_base():
    input_dir = config.RAW_DATA_PATH

    logger.info(f"Processing documents from: {input_dir}")
    all_documents: List[Document] = []
    document_loader = UnifiedDocumentLoader()

    for file_path in Path(input_dir).rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in config.SUPPORTED_FORMATS:
            try:
                # 1. 加载文档
                documents = document_loader.load_and_split_documents(str(file_path))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")

    if not all_documents:
        logger.warning("No documents found or all failed to process.")
        return

    logger.info(f"Successfully processed {len(all_documents)} document chunks.")

    # 
    embedding_model = VLLMEmbedding(model_name=config.EMBEDDING_MODEL_PATH)
    create_vector_store(all_documents, embedding_model)

    logger.info("Knowledge base creation complete.")


if __name__ == "__main__":
    build_offline_knowledge_base()
