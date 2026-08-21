import json
import time
from abc import ABC, abstractmethod
from tool.logger import logger
from tool.task_utils import update_task_status, add_running_task, add_done_task, add_node_duration


class NodeBase(ABC):

    name = 'NodeBase'


    # 这是创建实例自动生成的
    def __init__(self):
        if self.name == 'NodeBase':
            raise Exception('你妈逼名字都没有???')


    # 后面子类来实现的抽象方法
    @abstractmethod
    def process(self,state):
        pass


    def __call__(self,state):
        try:
            task_id = state['task_id']
            logger.info('开始处理任务')
            start_time=time.time()
            add_running_task(task_id,self.name)
            res = self.process(state)
            logger.info('处理任务完成')
            end_time = time.time()
            add_done_task(task_id,self.name)
            add_node_duration(task_id,self.name,end_time-start_time)
            return res
        except Exception as e:
            logger.info(f'报错了 只因 : {e}')
            raise e







