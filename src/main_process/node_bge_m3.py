import json
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.embedding_stuff import embedding_work
from tool.json_format import json_format
from tool.logger import logger


class node_bge_m3(NodeBase):

    name = 'node_bge_m3'
    def process(self,state:ImportGraphState):
        chunks = state.get('chunks')
        if not chunks:
            logger.error('chunks is empty')
            raise Exception('chunks is empty')
        # print(type(chunks))
        # 批处理 此时这个range拿到的是数字啊啊啊啊
        for i in range(0, len(chunks), 3):
            # 拿到3元切片
            # 切片是他妈的浅拷贝
            chunk_plus_3 = chunks[i:i + 3]
            # print(chunk_plus_3)
            # 整合内容列表
            chunk_content = [f"{chunk.get('item_name')}{chunk.get('sec_con')}" for chunk in chunk_plus_3]
            # print(chunk_content)
            # 扔给大模型
            res = embedding_work(chunk_content)
            # print(json_format(res))
            for idx, chunk in enumerate(chunk_plus_3):
                chunk['dense'] = res.get('dense')[idx]
                chunk['sparse'] = res.get('sparse')[idx]
        with open(r'D:\kb_pro_imitation\output\hak180产品安全手册\chunk_vec.json', 'w', encoding='utf-8') as f:
            f.write(json_format(chunks))
        return {
            'chunks': chunks
        }


if __name__ == '__main__':
    with open(r'D:\kb_pro_imitation\output\万用表RS-12的使用\chunk_item_nigger.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    init_state ={
        **chunks
    }
    node = node_bge_m3()
    res = node(init_state)
