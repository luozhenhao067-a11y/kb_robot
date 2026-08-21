from langchain.chat_models import init_chat_model
from config.config import milvus_client_config
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.embedding_stuff import embedding_work
from tool.json_format import json_format
from tool.logger import logger
from tool.milvus_client import create_reqs, search_hybrid
from tool.prompt import HYDE_PROMPT


class search_hyde(NodeBase):
    name = 'search_hyde'
    def process(self,state:ImportGraphState):
        rewritten_query = state.get('rewritten_query')
        if not rewritten_query:
            logger.info('rewritten_query is None')
            raise Exception('rewritten_query is None')
        item_names = state.get('item_names')
        if not item_names:
            logger.info('item_names is None')
            raise Exception('item_names is None')
        llm = init_chat_model(
            model = 'deepseek-ai/DeepSeek-V4-Pro',
            model_provider='openai',
        )
        message = [
            {'role': 'user', 'content': HYDE_PROMPT.format(rewritten_query=rewritten_query)},
        ]
        res = llm.invoke(message)
        hyde_answer = res.content
        merged_answer = f'{rewritten_query}\n{hyde_answer}'
        hyde_embeddings = embedding_work([rewritten_query])
        dense = hyde_embeddings.get('dense')[0]
        sparse = hyde_embeddings.get('sparse')[0]
        item_names = [
            item_name.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
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
            output_fields=['id', 'sec_title', 'item_name', 'file_title', 'sec_con']
        )
        # print(res)
        hyde_embedding_chunks = [
            {
                **i.get('entity', {}),
                'score': i.get('distance'),
                'source': 'local'
            }
            for i in res[0]
        ]
        print(json_format(res))
        return {
            'hyde_embedding_chunks': hyde_embedding_chunks,
        }



if __name__ == "__main__":
    init_state = {
    "rewritten_query": "关于BrotherHAK180烫金机如何使用",
    "item_names": ["兄弟HAK180烫金机"]  # 这里 是自己写的标准名称
    }
    node = search_hyde()
    result = node(init_state)
    logger.info(json_format(result))