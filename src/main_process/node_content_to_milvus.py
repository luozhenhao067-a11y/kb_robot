import json
from pymilvus import DataType, MilvusClient
from config.config import milvus_client_config
from main_process.base import NodeBase
from tool.logger import logger
from main_process.state import ImportGraphState
from tool.milvus_client import get_milvus_client


class node_content_to_milvus(NodeBase):
    name = 'node_content_to_milvus'
    def process(self,state:ImportGraphState):
        # 防御性编程
        chunks = state.get('chunks')
        # print(chunks)
        if not chunks:
            logger.error('chunks is empty')
            raise Exception('chunks is empty')
        # 搞个milvus
        collection_name, milvus_client = self.get_milvus()

        self.insert_milvus(chunks, collection_name, milvus_client)

        return {'chunks': chunks}

    def insert_milvus(self, chunks: list, collection_name: MilvusClient, milvus_client: str | None):
        file_title = chunks[0].get('file_title')
        safe_title = file_title.replace("'", "\\'").replace('"', '\\"').replace('\\', '\\\\')
        milvus_client.load_collection(collection_name)
        # 看有没有和file_title同名的内容  删行而不是删collection
        if milvus_client.has_collection(collection_name):
            milvus_client.delete(collection_name=collection_name, filter=f"file_title == '{safe_title}'")
        res = milvus_client.insert(collection_name=collection_name, data=chunks)
        ids = res.get('ids')
        if ids:
            for idx, chunk in enumerate(chunks):
                chunk['id'] = ids[idx]

    def get_milvus(self) -> tuple[MilvusClient, str | None]:
        milvus_client = get_milvus_client()
        collection_name = milvus_client_config.chunks_collection
        if not milvus_client:
            logger.error('milvus client is none')
            raise Exception('milvus client is none')
        schema = milvus_client.create_schema(
            auto_id=True
        ).add_field(
            field_name='id',
            datatype=DataType.INT64,
            is_primary=True
        ).add_field(
            field_name='part',
            datatype=DataType.INT64,
        ).add_field(
            field_name='sec_title',
            datatype=DataType.VARCHAR,
            max_length=100
        ).add_field(
            field_name='item_name',
            datatype=DataType.VARCHAR,
            max_length=100
        ).add_field(
            field_name='file_title',
            datatype=DataType.VARCHAR,
            max_length=100
        ).add_field(
            field_name='sec_con',
            datatype=DataType.VARCHAR,
            max_length=10000
        ).add_field(
            field_name='dense',
            datatype=DataType.FLOAT_VECTOR,
            dim=1024
        ).add_field(
            field_name='sparse',
            datatype=DataType.SPARSE_FLOAT_VECTOR,
        )

        index_params = milvus_client.prepare_index_params(
            collection_name=collection_name
        )
        index_params.add_index(
            field_name='dense',
            index_type='AUTOINDEX',
            metric_type='COSINE'
        )
        index_params.add_index(
            field_name='sparse',
            index_type='SPARSE_INVERTED_INDEX',
            metric_type='IP',
            params={
                "inverted_index_algo": "DAAT_MAXSCORE",
                # 高效的稀疏检索算法 提升性能的
                "normalize": True,
                # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度
                "quantization": "none"  # 精度压缩 (我们压缩过了)
                # ↑ 关闭量化，保持原始精度：模型生成的向量已经压缩的一半的精度了（BGE_FP16=1），这里就不再压缩了
                # "quantization": "none" → 存储原始向量，不压缩
                # "quantization": "sq8" → 存储压缩后的向量（8-bit 量化
            },
        )
        milvus_client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )
        return collection_name, milvus_client


if __name__ == '__main__':
    node = node_content_to_milvus()
    with open(r'D:\kb_pro_imitation\output\万用表RS-12的使用\chunk_vec.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    init_state = {
        'chunks': chunks
    }
    res = node.process(init_state)
