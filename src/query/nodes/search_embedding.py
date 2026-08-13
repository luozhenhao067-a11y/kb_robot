from config.config import milvus_client_config
from main_process.base import NodeBase
from tool.embedding_stuff import embedding_work
from tool.json_format import json_format
from tool.logger import logger
from tool.milvus_client import create_reqs, search_hybrid


class search_embedding(NodeBase):
    name = 'search_embedding'
    def process(self,state):
        rewritten_query = state.get('rewritten_query')
        item_names = state.get('item_names')
        if not rewritten_query:
            logger.info('捏妈问题都妹得')
            raise Exception('捏妈问题都妹得')
        if not item_names:
            logger.info('捏妈名字都妹得')
            raise Exception('捏妈名字都妹得')
        embeddings = embedding_work([rewritten_query])
        dense = embeddings.get('dense')[0]
        sparse = embeddings.get('sparse')[0]
        item_names = [
            item_name.replace('\\','\\\\').replace('"','\\"').replace("'","\\'")
            for item_name in item_names
        ]
        expr = f"item_name in {json_format(item_names)}"
        collection_name = milvus_client_config.chunks_collection
        reqs = create_reqs(
            dense, sparse,
            dense_anns_field='dense', sparse_anns_field='sparse',
            limit=10,
            expr=expr
        )
        res = search_hybrid(
            collection_name, reqs, ranker=(0.8, 0.2), limit=10,
            output_fields=['id','sec_title','item_name','file_title','sec_con']
        )
        # print(res)
        embedding_chunks = [
            {
                **i.get('entity', {}),
                'score': i.get('distance'),
                'source':'local'
            }
            for i in res[0]
        ]
        return {
            'embedding_chunks': embedding_chunks,
        }



if __name__ == "__main__":
    init_state = {
    "rewritten_query": "关于BrotherHAK180烫金机如何使用",
    "item_names": ["兄弟HAK180烫金机"]  # 这里 是自己写的标准名称
    }
    node = search_embedding()
    result = node(init_state)
    logger.info(json_format(result))