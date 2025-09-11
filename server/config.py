import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# --- MODEL ---
REASONING_MODEL_PATH = "/NAS/caizj/models/deepseek/DeepSeek-R1-Distill-Qwen-1.5B/"
EMBEDDING_MODEL_PATH = "/NAS/caizj/models/qwen/Qwen3-Embedding-0.6B/"

# --- DATASET ---
RAW_DATA_PATH = "/NAS/caizj/project/Awesome-MRAG/dataset/raw_data"

# --- Milvus ---
MILVUS_URI = "/NAS/caizj/project/Awesome-MRAG/dataset/milvus/mrag_milvus.db"
MILVUS_COLLECTION_NAME = "mrag_collection"

# --- RAG ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_TOP_K = 5

# --- FastAPI ---
API_HOST = "0.0.0.0"
API_PORT = 8992

# --- Document format ---
SUPPORTED_FORMATS = ['.pdf']