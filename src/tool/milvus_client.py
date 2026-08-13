from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker
from config.config import milvus_client_config

_milvus_client = None

def get_milvus_client():
    global _milvus_client
    if not _milvus_client:
        _milvus_client =MilvusClient(
            uri = milvus_client_config.milvus_url,
        )
    return _milvus_client

# 混合检索里面有个参数 是请求对象
def create_reqs(dense,sparse,
                dense_anns_field=None,sparse_anns_field=None,
                limit =10,
                dense_param=None,sparse_param=None,
                expr =None):
    # 方法记得和前面存库匹配!!!最好从头到尾只用一个方法
    if not dense_param:
        dense_param = {'metric_type': 'COSINE',}  # 写个匹配原则
    if not sparse_param:
        sparse_param = {'metric_type': 'IP',}
    dense_req = AnnSearchRequest(
        data = [dense],
        anns_field = dense_anns_field,
        param= dense_param,
        limit=limit,
        expr=expr,
    )
    sparse_req = AnnSearchRequest(
        data=[sparse],
        anns_field=sparse_anns_field,
        param=sparse_param,
        limit=limit,
        expr=expr,
    )
    return [dense_req, sparse_req]

def  search_hybrid(collection_name,reqs,ranker=(0.5,0.5),limit=10,output_fields=None):
    milvus_client = get_milvus_client()
    weight_ranker = WeightedRanker(ranker[0],ranker[1])
    res = milvus_client.hybrid_search(
        collection_name = collection_name,
        reqs  = reqs,
        ranker=weight_ranker,
        limit=limit,
        output_fields = output_fields,
        )
    return res

    