import config
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from loguru import logger
from langchain_core.runnables import RunnableLambda

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_chat_model():
    return ChatOpenAI(
        openai_api_base="http://localhost:8888/v1",
        api_key="EMPTY",
        model_name=config.REASONING_MODEL_PATH,
        temperature=0.8,
    )

def retrieve_and_format(retriever,query):
    documents = retriever.invoke(query)
    return {"documents":documents, "question":query}

def create_rag_chain(retriever):
    logger.info("Init RAG chain")

    chat_model = create_chat_model()
    prompt = hub.pull("rlm/rag-prompt") # 该官方Prompt需要{"context","question"}俩个参数
    rag_chain = (
        RunnableLambda(lambda query: retrieve_and_format(retriever, query))
        | {
            "context": lambda x: format_docs(x["documents"]),
            "question": lambda x: x["question"],
            "sources": lambda x: x["documents"],
        }
        | {
            "response": prompt | chat_model | StrOutputParser(),
            "sources": lambda x: x["sources"],
        }
    )

    logger.info("RAG链创建完成")
    return rag_chain
