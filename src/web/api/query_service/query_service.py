import json
import uuid
import fastapi
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Path
from fastapi import Body
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from query.fuck_nigger import fuck_nigger
from tool.mongo_client import get_recent_history_list, clear_history
from tool.task_utils import update_task_status, TASK_STATUS_PROCESSING, TASK_STATUS_COMPLETED, put_data_to_queue, \
    create_queue, get_task_info, TASK_STATUS_FAILED, get_data_from_queue

app=FastAPI(
    title='对话入口宝贝',
    description='用来他妈聊天的',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get('/history/{session_id}')
#session_id 前端生成 谁工作谁生成 注意session_id的一致性
async def history(session_id: str=fastapi.Path(...,description='会话id')):
    # 获取历史记录并返回
    history_list=get_recent_history_list(session_id)
    # 返回的是他妈游标对象 改成他妈的字典列表
    history_list=[{
        "_id": str(item.get("_id")),
        "role": item.get("role", ""),
        "text": item.get("text", ""),
        "rewritten_query": item.get("rewritten_query", ""),
        "item_names": item.get("item_names", ""),
        "ts": item.get("ts", ""),
        "session_id": item.get("session_id", "")
    } for item in history_list]
    # 排个序,懂?
    history_list.sort(key=lambda x: x["ts"])
    return {'items': history_list}

@app.delete('/history/{session_id}')
async def delete_history(session_id: str=fastapi.Path(...,description='会话id')):
    clear_history(session_id)
    # 没显示是前端没管返回
    return {'delete_all': '我他妈清完了'}
class Query(BaseModel):
    query:str=Field(...,description='要问的问题')
    session_id:str=Field(...,description='会话id')

def really_nigger(task_id,original_query,session_id):
    q=create_queue(task_id)
    try:
        init_state={
            'task_id': task_id,
            'session_id': session_id,
            'original_query': original_query,
        }
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        put_data_to_queue(task_id,'progress',get_task_info(task_id))
        fuck_nigger.create_and_run(init_state)
        update_task_status(task_id,TASK_STATUS_COMPLETED)
        put_data_to_queue(task_id,'progress',get_task_info(task_id))
    except Exception as e:
        update_task_status(task_id,TASK_STATUS_FAILED)
        put_data_to_queue(task_id,'error',get_task_info(task_id))
        raise e

@app.post('/query')
async def query(
        background_tasks: BackgroundTasks,
        query: Query=Body(...,description='查询请求体')):
    original_query=query.query
    session_id=query.session_id
    task_id=str(uuid.uuid4())
    # 后台直接开干啊
    background_tasks.add_task(really_nigger,task_id,original_query,session_id)
    return {
        'task_id': task_id,
        'session_id': session_id,
        # 'original_query': original_query,
    }

# 前端问后端 后端返回
@app.get('/stream/{task_id}')
async def stream(task_id:str =Path(...,description='任务id')):
    def generate_stream(task_id):
        while True:
            msg=get_data_from_queue(task_id)
            yield f'event:{msg.get("event")}\n'
            yield f'data:{json.dumps(msg.get("data"),ensure_ascii=False)}\n\n'
    return StreamingResponse(
        generate_stream(task_id),
        media_type='text/event-stream',
    )


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)