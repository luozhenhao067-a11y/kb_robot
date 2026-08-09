from typing import List
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from config.config import bge_m3
from tool.json_format import json_format
from tool.logger import logger

bge_m3_model = None

def call_embedding():
    global bge_m3_model
    if not bge_m3_model:
        bge_m3_model = BGEM3EmbeddingFunction(
            model_name = bge_m3.bge_m3_path,
            device = bge_m3.bge_device,
            use_fp16 = bge_m3.bge_fp16
        )
    return  bge_m3_model

def embedding_work(texts:List[str]):
    bge_m3_model = call_embedding()
    res = bge_m3_model.encode_documents(texts)
    return {
        'dense': [i.tolist() for i in res.get('dense')],
        'sparse': [dict(zip(i.indices.tolist(),i.data.tolist())) for i in res.get('sparse')]
    }


if __name__ == '__main__':
    texts = ['fuck you nigger ', 'go work']
    result = embedding_work(texts)
    logger.info(json_format(result))