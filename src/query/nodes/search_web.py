import json

from agents.mcp import MCPServerStreamableHttp
from config.config import mcp_config
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.json_format import json_format
from tool.logger import logger




class search_web(NodeBase):
    name = "search_web"
    def process(self, state:ImportGraphState):
        rewritten_query = state.get("rewritten_query")
        if not rewritten_query:
            logger.info('rewritten_query不能为空')
            raise Exception('rewritten_query不能为空')


        import asyncio
        res = asyncio.run(self.run_mcp(rewritten_query,limit=10))
        # print(res,type(res))
        search_res  = json.loads(res.content[0].text).get('pages')
        # print(search_res)
        web_search_docs = [{
            'title': i.get('title'),
            'content' : i.get('snippet'),
            'url': i.get('url'),
            'source':'web'
        } for i in search_res]
        return {
            'web_search_docs':web_search_docs
        }






    async def run_mcp(self,query,limit) -> None:
        token = mcp_config.api_key
        async with MCPServerStreamableHttp(
                name="Streamable HTTP Python Server",
                params={
                    "url": mcp_config.mcp_base_url,
                    "headers": {"Authorization": f"Bearer {token}"},
                    "timeout": 10,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
                client_session_timeout_seconds=30
        ) as server:
            res = await server.call_tool(
                tool_name='bailian_web_search',
                arguments={
                    'query': query,
                    'limit': limit,
                })
            return res


if __name__ == "__main__":
    init_state = {
        "rewritten_query": "关于BrotherHAK180烫金机如何使用"
    }
    # 执行节点的业务调用
    node_web_search_mcp = search_web()
    result = node_web_search_mcp(init_state)
    logger.info(json_format(result))