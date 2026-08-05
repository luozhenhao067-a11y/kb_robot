import re
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.json_format import json_format
from tool.logger import logger


class node_content_split(NodeBase):
    name = 'node_content_split'
    # 防御性编程
    def process(self,state: ImportGraphState):
        md_path = state.get('md_path')
        if not md_path:
            logger.info('我他妈服了几把md地址都不给')
            raise Exception('我他妈服了几把md地址都不给')
        md_path_obj = Path(md_path)  # obj的意思是地址对象  没有就是字符串
        if not md_path_obj.exists():
            logger.info('我他妈服了几把md地址不存在')
            raise Exception('我他妈服了几把md地址不存在')
        with open(md_path_obj, 'r', encoding='utf-8' )  as f:
            md_content = f.read()
        if not md_content:
            logger.info('我他妈服了几把md没内容')
            raise Exception('我他妈服了几把md没内容')
        # 换换行符
        file_title = md_path_obj.stem
        md_content = md_content.replace('\r\n', '\n').replace('\r', '\n')
        # 粗切
        md_line_list = md_content.split('\n')
        code_pattern = re.compile(r'(?:```|~~~)(\w+)?\s*\n([\s\S]*?)(?:```|~~~)')
        title_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        sign_before = False
        marked = ''
        pre_idx = 0
        sec_list = []
        for idx , line in enumerate(md_line_list):
            # 先他妈除臭  空格阴没边了
            line = line.strip()
            code_match = code_pattern.match(line)
            # 先看是不是代码块
            if code_match: # 有代码标识
                if sign_before == True:  #之前有标识
                    if marked == code_match.group(1): # 且标识相等
                        sign_before = False
                        marked = ''
                else: # 之前没有标识
                    sign_before = True
                    marked = code_match.group(1)
            # 不是代码而且是标题
            title_match = title_pattern.match(line)
            if sign_before == False and title_match: #  带'# '的被捕捉,目前在idx
                pre_line_list = md_line_list[pre_idx:idx]
                pre_con  = '\n'.join(pre_line_list) # 整合成文
                sec_list.append({
                    # 注意第一行没标题
                    'sec_title': pre_line_list[0] if pre_con.startswith('#') else '无题',
                    'file_title': file_title,
                    'sec_con': pre_con,
                })
                pre_idx = idx

        # 此时还剩最后一段
        sec_list.append({
            'sec_title': md_line_list[pre_idx],
            'file_title': file_title,
            'sec_con': '\n'.join(md_line_list[pre_idx:])
        })
        # 接下来递归细切
        chunk_size = 200
        chunk_overlap = 20
        spliter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ". ", "；", "; ", " ", ""],
        )
        final_sec_list = []  # 命名要清楚 讲究 多写点
        for sec in sec_list:
            # 对于每一个小节 去头
            sec_title = sec.get('sec_title')
            sec_con = sec.get('sec_con')
            real_con = sec_con[len(sec_title):] if  sec_con.startswith('#') else  sec_con   # 有些没标题
            # 表格 太短 不用分
            if len(real_con) < chunk_size:
                final_sec_list.append({
                    **sec,
                    'part':0 ,
                })
                continue
            if '<table' in real_con:
                final_sec_list.append({
                    **sec,
                    'part':0 ,
                })
                continue
            part_list =  spliter.split_text(real_con)
            for idx , part in enumerate(part_list):
                final_sec_list.append({
                    'sec_title': sec_title,
                    'file_title':file_title,
                    'sec_con':part,
                    'part':idx,
                })
        # 存个json
        json_path = md_path_obj.parent / ' 分号段了准备存向量库了.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json_format(final_sec_list))
        return {
            'chunks': final_sec_list
        }


if __name__ == '__main__':
    node = node_content_split()
    init_state = {
        'md_path': r'D:\kb_pro_imitation\output\万用表RS-12的使用\万用表RS-12的使用_new.md',
    }
    res = node.process(init_state)
    print(json_format(res))
















if __name__ == '__main__':
    node = node_content_split()
    init_state = {
        'md_path': r'D:\kb_pro_imitation\output\万用表RS-12的使用\万用表RS-12的使用_new.md',
    }
    res = node(init_state)

