from datetime import datetime
import pathlib
import shutil
import uuid

import fastapi
import uvicorn
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from config.config import minio_config, rerank_config
from main_process.fuck_you_nigger import main_process
from tool.logger import logger
from tool.minio_client import get_minio_client
from tool.task_utils import update_task_status, TASK_STATUS_PROCESSING, TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, \
    get_task_info

app=FastAPI(
    title="导入文件的地方,懂?",
    description='这是导文件的入口',
    version="1.0.0",
)

# 跨域问题一句话解决
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fuck_you_nigger(task_id,local_dir,local_file_path):
    try:
        init_state={
            'task_id':task_id,
            'local_dir':local_dir,
            'local_file_path':local_file_path,
        }
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        main_process.create_and_run(init_state)
        update_task_status(task_id,TASK_STATUS_COMPLETED)
    except Exception as e:
        logger.error('我他妈操了,这个graph他妈失败了')
        update_task_status(task_id,TASK_STATUS_FAILED)
        raise e


# POST http://127.0.0.1:8000/upload 有方法有接口
@app.post("/upload")
async def upload(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...,description='上传的文件啊')):
    task_id=str(uuid.uuid4())
    # 接收文件保存本地
    local_dir=rf'D:\kb_pro_imitation\output\{datetime.now().strftime("%Y%m%d")}'
    local_dir_obj= pathlib.Path(local_dir)
    if not local_dir_obj.exists():
        # 如果不存在 递归创建
        local_dir_obj.mkdir(parents=True, exist_ok=True)
    local_file_path=str(local_dir_obj/file.filename)  # 等下open里要是字符串
    with open(local_file_path,'wb') as f:
        # 写入文件用shutil(处理大文件)
        shutil.copyfileobj(file.file,f,1024*1024)
    logger.info('哈哈哈哈文件他妈的写入本地啦')
    # 备份minio
    minio_client=get_minio_client()
    minio_client.fput_object(
        bucket_name=minio_config.minio_bucket_name,
        # 除了桶之外的
        object_name=f'pdf_file/{datetime.now().strftime("%Y%m%d")}/{task_id}/{file.filename}',
        file_path=local_file_path
    )
    # 后台跑graph
    background_tasks.add_task(fuck_you_nigger,task_id,local_dir,local_file_path)
    return {
        'task_id':task_id,
        'local_file_path':local_file_path,
    }

# 搞个轮询的接口
#http://127.0.0.1:8000/status/799b6a16-5207-4eb1-8b07-48184b604a6f
@app.get("/status/{task_id}")
async def get_status(task_id: str= fastapi.Path(..., description='任务id')):
    # 给前端返状态
    return get_task_info(task_id)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
