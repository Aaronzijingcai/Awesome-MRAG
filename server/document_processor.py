import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders.parsers.pdf import PyPDFium2Parser

import config
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger


class UnifiedDocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
        )

    # 加载PDF文件
    # 输入PDF路径，输出List[Document]
    def load_pdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        PDFs = []
        for i, page in enumerate(pages):
            doc = Document(
                page_content=page.page_content,
                metadata={
                    "file_name": os.path.basename(file_path),
                    "source_location": f"第{i + 1}页",
                    "minio_id": 444, 
                },
            )
            PDFs.append(doc)

        logger.info(f"成功提取PDF文档 {os.path.basename(file_path)} - {len(pages)} 页")
        return PDFs
    
    # 
    def load_and_split_documents(self, input_path: str) -> List[Document]:
        if os.path.isfile(input_path):
            documents = self.load_document(input_path)
        elif os.path.isdir(input_path):
            documents = self._load_directory(input_path)
        else:
            raise ValueError(f"输入路径不存在: {input_path}")

        # 分割文档
        splits = self.text_splitter.split_documents(documents)

        # 添加chunk信息
        for i, split in enumerate(splits):
            split.metadata["chunk_id"] = i
            split.metadata["chunk_size"] = len(split.page_content)

        logger.info(f"文档被分割成 {len(splits)} 个文本块")
        return splits

    # 加载单个文件
    def load_document(self, file_path: str) -> List[Document]:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self.load_pdf(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {extension}")

    # 加载文件夹
    def _load_directory(self, directory_path: str) -> List[Document]:
        """加载目录中的所有文档"""
        all_documents = []
        directory = Path(directory_path)

        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in config.SUPPORTED_FORMATS
            ):
                try:
                    documents = self.load_document(str(file_path))
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {e}")

        return all_documents

