from pathlib import Path
from typing import List

import config
from document_processor import UnifiedDocumentLoader
from langchain_core.documents import Document
from loguru import logger
from vector_store import VLLMEmbedding, create_vector_store, load_existing_vector_store

# 离线初始化本地知识库
def build_offline_knowledge_base():
    input_dir = config.RAW_DATA_PATH

    logger.info(f"Processing documents from: {input_dir}")
    all_documents: List[Document] = []
    document_loader = UnifiedDocumentLoader()

    for file_path in Path(input_dir).rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in config.SUPPORTED_FORMATS:
            try:
                # 1. 将所有文件变成Chunk级Document对象，放入all_documents中
                documents = document_loader.load_and_split_documents(str(file_path))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")

    if not all_documents:
        logger.warning("No documents found or all failed to process.")
        return

    logger.info(f"Successfully processed {len(all_documents)} document chunks.")

    # 对all_documents进行Embedding，并存入Milvus中
    embedding_model = VLLMEmbedding(model_name=config.EMBEDDING_MODEL_PATH)
    create_vector_store(all_documents, embedding_model)

    logger.info("Knowledge base creation complete.")

# 本地知识库动态新增
def update_offline_knowledge_base():
    update_dir = Path(config.UNUPDATED_DATA_PATH)

    # 1.获取所有待更新文件
    files = [f for f in update_dir.rglob("*") 
             if f.is_file() and f.suffix.lower() in config.SUPPORTED_FORMATS]
    
    if not files:
        logger.info("No files to update.")
        return
    
    logger.info(f"Found {len(files)} files to update")

    # 2. 加载向量库和文档处理器
    embedding_model = VLLMEmbedding(model_name=config.EMBEDDING_MODEL_PATH)
    vector_store = load_existing_vector_store(embedding_model)
    document_loader = UnifiedDocumentLoader()

    # 3. 处理文件
    for file_path in files:
        file_name = file_path.name
        try:
            # 检查是否已存在（根据文件名搜索）
            existing = vector_store.similarity_search(
                query="", k=1, expr=f'file_name == "{file_name}"'
            )
            
            if existing:
                logger.warning(f"File {file_name} already exists, skipping")
                continue
            
            # 加载、分割、添加文档
            documents = document_loader.load_and_split_documents(str(file_path))
            vector_store.add_documents(documents)
            
            # 删除源文件
            file_path.unlink()
            logger.info(f"✅ Successfully added and removed {file_name} ({len(documents)} chunks)")
            
        except Exception as e:
            logger.error(f"Failed to process {file_name}: {e}")
    
    logger.info("Knowledge base update complete.")


if __name__ == "__main__":
    build_offline_knowledge_base()
    # update_offline_knowledge_base()

