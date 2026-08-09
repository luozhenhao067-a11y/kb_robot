from pymilvus import MilvusClient
from config.config import milvus_client_config

_milvus_client = None

def get_milvus_client():
    global _milvus_client
    if not _milvus_client:
        _milvus_client =MilvusClient(
            uri = milvus_client_config.milvus_url,
        )
    return _milvus_client