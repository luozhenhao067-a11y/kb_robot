import json
from langchain.chat_models import init_chat_model
from config.config import milvus_client_config
from query.base import NodeBase
from query.state import QueryGraphState
from tool.embedding_stuff import embedding_work
from tool.json_format import json_format
from tool.logger import logger
from tool.milvus_client import get_milvus_client, create_reqs, search_hybrid
from tool.mongo_client import add_or_update_history, get_recent_history_list, update_item_names_and_query
from tool.prompt import ITEM_NAME_EXTRACT_SYSTEM_PROMPT, ITEM_NAME_EXTRACT_TEMPLATE


class know_the_fucking_item(NodeBase):
    name = 'know_the_fucking_item'
    def process(self,state:QueryGraphState):
        session_id = state['session_id']
        if not session_id:
            logger.info('你麻痹session_id给我啊')
            raise Exception('你麻痹session_id给我啊')
        original_query = state['original_query']
        if not original_query:
            logger.info('???他妈问题呢')
            raise Exception('???他妈问题呢')
        # 马上写入
        _id = add_or_update_history(session_id,'user',original_query)



        history_list = get_recent_history_list(session_id,limit=10)
        content_to_llm = ''
        for history in history_list:
            role = history['role']
            text = history['text']
            content = f'{role},{text}\n'
            content_to_llm += content
        # print(content_to_llm)
        llm = init_chat_model(
            model='deepseek-ai/DeepSeek-V4-Pro',
            model_provider='openai'
        )
        # 提示词很重要
        message = [
            {"role": "system", "content": ITEM_NAME_EXTRACT_SYSTEM_PROMPT},
            {"role": "user",
             "content": ITEM_NAME_EXTRACT_TEMPLATE.format(history_text=content_to_llm, original_query=original_query)},
        ]
        res = llm.invoke(message)
        print(res.content,type(res.content))
        res_json = res.content
        if res_json.startswith('```json'):
            res_json = res_json.replace('```json','').replace('```','')
        res_dict = json.loads(res_json)
        # 这个item_names是他妈的有可能多个的 你一句话说了多个商品
        item_names = res_dict.get('item_names',[])
        rewritten_query = res_dict['rewritten_query']
        if item_names:
            item_names  =  [item_name.replace(' ','').replace('\n','').replace('\t','')
             for item_name in item_names]
        if not rewritten_query:
            rewritten_query = original_query


        answer = ''
        final_item_names = []
        if item_names:
            #  把大模型 总结的名字向量化 去和之前存的匹配
            embeddings  = embedding_work(item_names)
            milvus_client  = get_milvus_client()
            collection_name  = milvus_client_config.item_name_collection
            # 混合搜索一波
            final_search_item_list = []
            for idx,item_name in enumerate(item_names):
                dense = embeddings.get('dense')[idx]
                sparse = embeddings.get('sparse')[idx]
                reqs = create_reqs(dense, sparse,dense_anns_field='dense',sparse_anns_field='sparse')
                res = search_hybrid(collection_name,reqs,(0.8,0.2),limit=10,output_fields=['item_name'])
                # print(json_format(res))
                search_item_name = [
                    {
                        'original_item_name': item_name,
                        'search_item_name':i.get('entity').get('item_name'),
                        'score':i.get('distance'),
                    }
                    for i in res[0]
                ]
                final_search_item_list.extend(search_item_name)
            print(final_search_item_list)
            # 对齐 比分数 分类
            confirm_item_name = [
                i.get('search_item_name')
                for i in final_search_item_list
                if i.get('score') >= 0.85
            ]
            optional_item_name = [
                i.get('search_item_name')
                for i in final_search_item_list
                if i.get('score') < 0.85 and i.get('score') >=0.6
            ]
            if confirm_item_name:
                final_item_names  = confirm_item_name
                answer =  ''
            elif optional_item_name:
                final_item_names = optional_item_name
                answer = f'你说的是他妈下面哪个{','.join(optional_item_name)}'
            else:
                answer = '他妈说的啥啊'


        # 有 answer 就需要添加历史
        if answer:
            _id = add_or_update_history(session_id,'assistant',answer)
        # 无论有没有answer都几把回填
        history_list = get_recent_history_list(session_id,limit=10)
        ids = [history.get('_id') for history in history_list]
        if ids:
            update_item_names_and_query(ids, item_names=final_item_names, rewritten_query=rewritten_query)

        return {
            'message_id': _id,
            'original_query': original_query,
            'answer': answer,
            'item_names': final_item_names,
            'rewritten_query': rewritten_query,
            'history': get_recent_history_list(session_id, limit=10)
        }



if __name__ == '__main__':
    session_id = "test_001"
    add_or_update_history(session_id, "user", "咨询下烫金机。")
    add_or_update_history(session_id, "assistant", "您好。请问是哪个型号")
    add_or_update_history(session_id, "user", "hak180")
    add_or_update_history(session_id, "assistant", "具体有什么问题呢？")
    init_state ={
        'session_id': session_id,
        'original_query':'我他妈要怎么用?'
    }
    node=know_the_fucking_item()
    res = node(init_state)
    print(json_format(res))