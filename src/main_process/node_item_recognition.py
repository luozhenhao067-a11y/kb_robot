import json
from typing import Any

from langchain.chat_models import init_chat_model
from pymilvus import DataType, MilvusClient
from config.config import milvus_client_config
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.embedding_stuff import embedding_work
from tool.json_format import json_format
from tool.logger import logger
from tool.milvus_client import get_milvus_client
from tool.prompt import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE


class node_item_recognition(NodeBase):
    name = "node_item_recognition"
    def process(self, state: ImportGraphState):
        chunks, file_title = self.check_state(state)
        item_name = self.get_item_name(chunks, file_title)
        collection_name, milvus_client = self.get_milvus()

        milvus_client.load_collection(collection_name=collection_name)
        safe_item_name = item_name.replace('\\','\\\\').replace('"','\\"').replace("'","\\'")
        # 删掉重名行
        milvus_client.delete(collection_name=collection_name, filter=f"item_name == '{safe_item_name}'")

        # 插入
        self.insert_milvus(collection_name, file_title, item_name, milvus_client)
        # 回填item_name到每个chunk
        for chunk in chunks:
            chunk['item_name'] = item_name

        return {
            'chunks': chunks,
        }

    def insert_milvus(self, collection_name: MilvusClient, file_title: str, item_name: str, milvus_client: str | None):
        embedding = embedding_work([item_name])
        dense = embedding.get('dense')[0]
        # print(dense)
        sparse = embedding.get('sparse')[0]
        data = [{
            "item_name": item_name,
            "file_title": file_title,
            "dense": dense,
            "sparse": sparse,
        }]

        milvus_client.insert(
            collection_name=collection_name,
            data=data
        )

    def get_milvus(self) -> tuple[MilvusClient, str | None]:
        milvus_client = get_milvus_client()
        if not milvus_client:
            logger.info('他妈创建milvus_client失败')
            raise Exception('他妈创建milvus_client失败')
        # 结构   index  创建
        collection_name = milvus_client_config.item_name_collection
        # 没人会删整个数据库的 这他妈是傻逼
        if not milvus_client.has_collection(collection_name):
            # schema就是为了传auto_id的
            schema = milvus_client.create_schema(
                auto_id=True,
            ).add_field(
                field_name="id",
                datatype=DataType.INT64,
                is_primary=True,
            ).add_field(
                field_name="item_name",
                datatype=DataType.VARCHAR,
                max_length=100,
            ).add_field(
                field_name='file_title',
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name='dense',
                datatype=DataType.FLOAT_VECTOR,
                dim=1024
            ).add_field(
                field_name='sparse',
                datatype=DataType.SPARSE_FLOAT_VECTOR,
            )
            index_params = milvus_client.prepare_index_params()
            index_params.add_index(
                field_name='dense',
                metric_type='COSINE',
                index_type='IVF_FLAT',
                params={"nlist": 128, 'nprobe': 10}
            )
            index_params.add_index(
                field_name='sparse',
                metric_type='IP',
                index_type='SPARSE_INVERTED_INDEX',
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    # 高效的稀疏检索算法 提升性能的
                    "normalize": True,
                    # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度
                    "quantization": "none"  # 精度压缩 (我们压缩过了)
                    # ↑ 关闭量化，保持原始精度：模型生成的向量已经压缩的一半的精度了（BGE_FP16=1），这里就不再压缩了
                    # "quantization": "none" → 存储原始向量，不压缩
                    # "quantization": "sq8" → 存储压缩后的向量（8-bit 量化
                }
            )

            milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
        return collection_name, milvus_client

    def get_item_name(self, chunks: list[Any], file_title: str) -> str:
        k = 10
        max_len = 10000  # 模型最大处理长度
        chunks_sample_list = chunks[:k]  # 取前10位
        content_2_model = '\n'
        for idx, chunk_sample in enumerate(chunks_sample_list):  # 对每一个chunk进行处理 标题加上内容
            chunk_title = chunk_sample.get('sec_title', '')
            chunk_content = chunk_sample.get('sec_con', '')
            chunk_text = f'[第{idx}个文本块]\n{file_title}\n{chunk_title}\n{chunk_content}'
            content_2_model += chunk_text
            if len(content_2_model) > max_len:
                logger.info('他妈太长了了了')
                break
        content_2_model = content_2_model[:max_len]
        llm = init_chat_model(
            model="Qwen/Qwen3.5-9B",
            model_provider="openai",
            temperature=0.7,
        )
        logger.info('开始识别主体')
        messages = [
            {"role": "system", "content": ITEM_NAME_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ITEM_NAME_USER_PROMPT_TEMPLATE.format(file_title=file_title, context=content_2_model)
            }
        ]
        res = llm.invoke(messages)
        logger.info(f'拿到结果{res}')
        item_name = res.content.replace('\n', '').replace(' ', '').replace('\t', '')
        return item_name

    def check_state(self, state: ImportGraphState) -> tuple[list, str]:
        chunks = state.get('chunks', [])
        file_title = state.get('file_title', '')
        if not chunks:
            logger.info(' 他妈空的 值都没有')
            raise Exception(' chunks is empty')
        if not file_title:
            logger.info(' 他妈空的 文件名都没有')
            raise Exception(' file_title is empty')
        logger.info('开始处理 chunks')
        return chunks, file_title


if __name__ == '__main__':
    node = node_item_recognition()
    with open(r'D:\kb_program\output\hak180产品安全手册\chunks.json', 'r', encoding='utf-8') as f:
        chunks_json = json.load(f)
    init_state = {
        'chunks': chunks_json,
        'file_title': 'hak180产品安全手册'
    }
    res = node(init_state)
    logger.info(f'拿到结果 {res}')
    with open(r'D:\kb_pro_imitation\output\万用表RS-12的使用\chunk_item_nigger.json', 'w', encoding='utf-8') as f:
        f.write(json_format(res))