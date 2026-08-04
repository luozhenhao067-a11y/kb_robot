import json
from pathlib import Path

from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.logger import logger


# START下面的第一个节点  判断是md还是pdf
class node_entry(NodeBase):

    name = 'node_entry'

    def process(self,state: ImportGraphState):
        local_file_path = self.check_path_file(state)
        # 判断文件类型
        file_title = Path(local_file_path).stem
        file_suffix = Path(local_file_path).suffix  # 后缀带点的
        if file_suffix.lower() == '.pdf':
            logger.info('破案,是pdf文件')
            return {
                'is_pdf_read_enabled': True,
                'local_file_path': local_file_path,
                'pdf_path' : local_file_path,
                'file_title': file_title,
            }
        elif file_suffix.lower() == '.md':
            logger.info('破案,是md文件')
            return {
                'is_md_read_enabled': True,
                'local_file_path': local_file_path,
                'md_path': local_file_path,
                'file_title': file_title,
            }
        else:
            logger.info('他妈的文件后缀不支持啊???另谋高就')
            raise Exception('他妈的文件后缀不支持啊???另谋高就')

    def check_path_file(self, state: ImportGraphState) -> str:
        # 无论什么节点  进来先防御性编程
        local_file_path = state.get('local_file_path', '')
        if not local_file_path:
            logger.info('他妈文件路径都没有啊,诗人???')
            raise Exception('他妈文件路径都没有啊,诗人???')
        logger.info('有路径了 我看看你路径里有没有文件')
        # 查看路径里的文件是否存在
        local_file_path_obj = Path(local_file_path).exists()
        if not local_file_path_obj:
            logger.info('路径里没有文件啊???')
            raise Exception('路径里没有文件啊???')
        logger.info('路径里文件存在 判断文件类型')
        return local_file_path


if __name__ == '__main__':
    entry = node_entry()
    init_state ={
        'local_file_path': r'D:\kb_pro_imitation\05-device_txt\doc\hak180产品安全手册.pdf',
    }
    res = json.dumps(entry(init_state), indent=4)

    logger.info(f'搞定了 ,破案结果:{res}')


