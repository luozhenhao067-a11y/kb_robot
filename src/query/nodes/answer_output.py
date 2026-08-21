import re
from langchain.chat_models import init_chat_model
from query.base import NodeBase
from tool.mongo_client import add_or_update_history
from tool.prompt import ANSWER_PROMPT
from tool.task_utils import put_data_to_queue


class answer_output(NodeBase):
    name="answer_output"
    def process(self,state  ):
        answer=state.get("answer")
        task_id=state.get("task_id")
        if answer:
            #  如果有答案了 一次性返回前端 最后出来的就是final
            # 前端final处理器要的是 {'answer': ...} 包,裸字符串会被 JSON.parse 成字符串读不到 answer
            put_data_to_queue(task_id,'final',{'answer': answer, 'image_urls': []})
        else:
            # 拿到相关搜索
            final_content=''
            chunks=state.get("reranked_docs")
            for idx,chunk in enumerate(chunks):
                title=chunk.get("title")
                content=chunk.get("content")
                url=chunk.get("url")
                source=chunk.get("source")
                chunk_final_content=f"{title}\n{url}\n{source}\n{content}\n\n"
                final_content+=chunk_final_content
            # 拿到所有历史
            histories_final_content=''
            histories=state.get("history")
            for history in histories:
                history_content=f"{history['role']}\n{history['text']}\n\n"
                histories_final_content+=history_content
            item_names=','.join(state.get("item_names"))
            rewritten_query=state.get("rewritten_query")
            message=[{
                'role':'user',
                'content':ANSWER_PROMPT.format(
                    context=final_content,
                    history=histories_final_content,
                    item_names=item_names,
                    question=rewritten_query
                )
            }][:10000]
            llm=init_chat_model(
                model="Qwen/Qwen3.5-9B",
                model_provider="openai",
                temperature=0.7,
            )
            res=llm.stream(message)
            answer=''
            for i in res:
                # 流式输出的就是delta
                # 前端delta处理器读的是 d.delta,必须包成对象,裸字符串读不到
                put_data_to_queue(task_id,'delta',{'delta': i.content})
                answer+=i.content
            the_fucking_pic_team=set()
            md_img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            for idx,chunk in enumerate(chunks):
                content=chunk.get("content","")
                content = "".join(content.strip())
                matches = md_img_pattern.findall(content)
                for match in matches:
                    img_url=match.strip()
                    if img_url and img_url not in the_fucking_pic_team:
                        the_fucking_pic_team.add(img_url)
            pic_team=list(the_fucking_pic_team)
            if answer:
                session_id=state.get("session_id")
                add_or_update_history(
                    session_id=session_id,
                    role='assistant',
                    text=answer,
                    rewritten_query=rewritten_query,
                    item_names=item_names,
                )
            put_data_to_queue(task_id,'final',{'answer': answer,'image_urls':pic_team})
        return {'answer':answer}

