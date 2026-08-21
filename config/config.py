import os
from dotenv import load_dotenv
# 记住要重写
load_dotenv(override= True)

class MinerUConfig:
    mineru_token = os.getenv("MINERU_TOKEN")


class ALI_config:
    ali_api_key = os.getenv("ALI_API_KEY")
    ali_base_url = os.getenv("ALI_BASE_URL")
    vl_name = os.getenv("VL_NAME")


class minio_config:
    minio_endpoint = os.getenv("MINIO_ENDPOINT")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")
    minio_img_dir = os.getenv("MINIO_IMG_DIR")


class bge_m3:
    bge_m3_path = os.getenv("BGE_M3_PATH")
    # BGE-M3 模型名称
    bge_m3 = os.getenv("BGE_M3")
    # 嵌入模型运行设备，cuda:0表示使用第1块GPU，cpu表示使用CPU，cuda:N表示第N+1块GPU
    bge_device = os.getenv("BGE_DEVICE")
    # 是否使用半精度（True/False）1=开启（GPU加速更高效），0=关闭（兼容低版本GPU/CPU）
    bge_fp16 = True if os.getenv("BGE_FP16") in ("1", "True",1,True) else False

class milvus_client_config:
    milvus_url = os.getenv('MILVUS_URL')
    # 知识库切片集合名
    chunks_collection = os.getenv('CHUNKS_COLLECTION')
    # 商品名称集合名
    item_name_collection = os.getenv('ITEM_NAME_COLLECTION')

class mongodb_config:
    mongo_url = os.getenv("MONGO_URL")
    mongo_db_name = os.getenv("MONGO_DB_NAME")


class mcp_config:
    mcp_base_url = os.getenv("MCP_DASHSCOPE_BASE_URL")
    api_key = os.getenv("ALI_API_KEY")


class rerank_config:
    rerank_base_url =os.getenv("RERANK_BASE_URL")
    rerank_api_key = os.getenv("RERANK_API_KEY")