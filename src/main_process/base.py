import json
from abc import ABC, abstractmethod
from tool.logger import logger


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
            logger.info('开始处理任务')
            res = self.process(state)
            logger.info('处理任务完成')
            return res
        except Exception as e:
            logger.info(f'报错了 只因 : {e}')
            raise e







