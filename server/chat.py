from typing import Any, Dict, List, Optional

import config
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field
from rag_chain import create_rag_chain
from vector_store import VLLMEmbedding, load_existing_vector_store
from mcp_manager import mcp_manager as mcp


class RAGRequest(BaseModel):
    query: str = Field(...)
    task_description: Optional[str] = Field(
        default="Given a search query, retrieve relevant passages that answer the query",
    )


class SourceDocument(BaseModel):
    page_content: str
    metadata: Dict[str, Any]


class RAGResponse(BaseModel):
    response: str
    sources: List[SourceDocument]


# Initialize RAG chain：embedding_model -> vector_store -> retriever -> rag_chain 
embedding_model = VLLMEmbedding(model_name=config.EMBEDDING_MODEL_PATH)
vector_store = load_existing_vector_store(embedding_model)
retriever = vector_store.as_retriever(search_kwargs={"k": config.RETRIEVER_TOP_K})

# 根据配置决定是否启用MCP
mcp_service = None
if config.ENABLE_WEB_SEARCH:
    try:
        from mcp_manager import mcp_manager
        if mcp_manager.initialize():
            mcp_service = mcp_manager
            logger.info("✅ MCP服务已启用")
    except Exception as e:
        logger.warning(f"MCP服务初始化失败: {e}")

rag_chain = create_rag_chain(retriever,mcp_service)
logger.info("✅ RAG service initialized successfully")



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1.FastAPI输入输出为BaseModel实体对象，需创建RAGRequest和RAGResponse对象
@app.post("/rag/query", response_model=RAGResponse)
async def rag_query_endpoint(request: RAGRequest):
    query_with_instruct = embedding_model.get_detailed_instruct(  # 2. Qwen3Embedding输入数据包括Instruct和Query
        task_description=request.task_description,
        query=request.query,
    )

    # 3. 区分embedding所需query和网络搜索所需query
    query_data = {
        "query_with_instruct": query_with_instruct,
        "original_query": request.query
    }

    result = rag_chain.invoke(query_data)  # 4. 执行rag_chain

    sources = []     # 5. 文档溯源
    for doc in result["sources"]:
        source_doc = SourceDocument(
            page_content=doc.page_content, metadata=doc.metadata
        )
        sources.append(source_doc)
    # 6. 组合response和sources给RAGResponse
    return RAGResponse(response=result["response"], sources=sources)


if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT, log_level="info")
