import config
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from loguru import logger
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# 组装本地知识和web知识
def build_context(retrieval_result):
    context = []

    local_docs = retrieval_result.get("local_docs", [])
    if local_docs:
        context.append(f"【本地知识库】\n{format_docs(local_docs)}")

    web_docs = retrieval_result.get("web_docs")
    if web_docs:
        context.append(f"【网络搜索】\n{web_docs}")

    return "\n\n---\n\n".join(context) if context else "未找到相关信息"


def build_sources(retrieval_result):
    sources = []

    # 本地知识
    for doc in retrieval_result.get("local_docs", []):
        doc.metadata["source_type"] = "local"
        sources.append(doc)

    # Web知识
    web_docs = retrieval_result.get("web_docs")
    if web_docs:
        web_doc = Document(
            page_content=web_docs[:500] if len(web_docs) > 500 else web_docs,
            metadata={"source_type": "web", "source_location": "网络搜索"},
        )
        sources.append(web_doc)

    return sources


def create_chat_model():
    return ChatOpenAI(
        openai_api_base="http://localhost:8888/v1",
        api_key="EMPTY",
        model_name=config.REASONING_MODEL_PATH,
        temperature=0.8,
    )


def retrieve_and_format(retriever, query_data, mcp_service=None):

    query_with_instruct = query_data["query_with_instruct"]
    original_query = query_data["original_query"]

    local_docs = retriever.invoke(query_with_instruct)

    web_docs = None
    if config.ENABLE_WEB_SEARCH and mcp_service and mcp_service.web_search_tool:
        web_docs = mcp_service.web_search(original_query)

    return {"local_docs": local_docs, "web_docs": web_docs, "question": original_query}


def create_rag_chain(retriever, mcp_service=None):
    logger.info("Init RAG chain")

    chat_model = create_chat_model()
    template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        RunnableLambda(lambda query_data: retrieve_and_format(retriever, query_data, mcp_service))
        | {
            "context": lambda x: build_context(x),
            "question": lambda x: x["question"],
            "sources": lambda x: build_sources(x),
        }
        | {
            "response": prompt | chat_model | StrOutputParser(),
            "sources": lambda x: x["sources"],
        }
    )

    logger.info("RAG链创建完成")
    return rag_chain
