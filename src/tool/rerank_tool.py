import dashscope
from http import HTTPStatus
from config.config import rerank_config
from tool.json_format import json_format
from tool.logger import logger

# 以下为华北2（北京）地域的配置，调用时请将{WorkspaceId}替换为真实的业务空间ID，各地域的配置不同。
dashscope.base_http_api_url = rerank_config.rerank_base_url
dashscope.api_key = rerank_config.rerank_api_key
def text_rerank(query,texts,limit=10):
    try:
        resp = dashscope.TextReRank.call(
            model="qwen3-rerank",
            query=query,
            documents=texts,
            top_n=limit,
            return_documents=True,
            instruct="Given a web search query, retrieve relevant passages that answer the query."
        )
        if resp.status_code == HTTPStatus.OK:
            # print(json_format(resp),type(resp))
            return [{'index':i.index,
                     'score':i.relevance_score}
                    for i in resp.output.results]
        else:
            logger.error('重排序失败')
            raise Exception(f'重排序失败{resp.status_code}')
    except Exception as e:
        raise e


if __name__ == '__main__':
    res = text_rerank("什么是文本排序模型",[
            "文本排序模型广泛用于搜索引擎和推荐系统中，它们根据文本相关性对候选文本进行排序",
            "量子计算是计算科学的一个前沿领域",
            "预训练语言模型的发展给文本排序模型带来了新的进展"
        ])
    print(json_format(res)) # 默认给你排好序了