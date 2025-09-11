from typing import List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_milvus import Milvus
from loguru import logger
from vllm import LLM

import config


class VLLMEmbedding(Embeddings):
    def __init__(self, model_name: str, **kwargs):
        super().__init__(**kwargs)
        self.model = LLM(model=model_name, task="embed")  # model参数指模型地址

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        outputs = self.model.embed(texts)
        return [output.outputs.embedding for output in outputs]

    def embed_query(self, text: str) -> list[float]:
        outputs = self.model.embed([text])
        return outputs[0].outputs.embedding

    def get_detailed_instruct(self, task_description: str, query: str) -> str:
        return f"Instruct: {task_description}\nQuery: {query}"  # Qwen3 Embedding需要该参数


def create_vector_store(
    documents: List[Document], embedding_model: VLLMEmbedding
) -> Milvus:
    vector_store = Milvus.from_documents(  # 创建vector_store需要指定document参数
        documents=documents,
        embedding=embedding_model,
        connection_args={"uri": config.MILVUS_URI},
        collection_name=config.MILVUS_COLLECTION_NAME,
        drop_old=True,
    )

    logger.info("Milvus vector store is built successfully")
    return vector_store


def load_existing_vector_store(embedding_model: VLLMEmbedding = None) -> Milvus:
    vector_store = Milvus(  # 使用vector_store无需指定document参数
        embedding_function=embedding_model,
        connection_args={"uri": config.MILVUS_URI},
        collection_name=config.MILVUS_COLLECTION_NAME,
    )
    
    logger.info("connecting to Milvus vector store successfully")
    return vector_store
