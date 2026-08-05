import re
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.json_format import json_format
from tool.logger import logger


class node_content_split(NodeBase):
    name = 'node_content_split'
    def process(self,state: ImportGraphState):
        # 进来检测就完了
        md_path = state.get('md_path', '')

        if not md_path:
            logger.info('他妈的md路径都没有啊,诗人???')
            raise Exception('他妈的md路径都没有啊,诗人???')
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            logger.info('md路径里没有文件啊???')
            raise Exception('md路径里没有文件啊???')
        # 都有取个content先
        with open(md_path_obj, 'r', encoding='utf-8') as f:
            md_content = f.read()
        if not md_content:
            logger.info('md文件里没有内容啊???')
            raise Exception('md文件里没有内容啊???')
        # 拿到content的第一件是就是先把换行符给我大一统(可以链式调用)
        file_title = md_path_obj.stem
        md_content = md_content.replace('\r\n', '\n').replace('\r', '\n')
        # 进行粗切操作
        # 按行切 得到行列表
        md_line_list = md_content.split('\n')
        code_pattern = re.compile(r'^(`{3,}|~{3,})')
        title_pattern = re.compile(r'^\s*#{1,6}\s+.+')
        code_block_before =  False # 之前是否出现过```或者~~~
        marker =  None
        pre_idx =0
        sec_list = []   # 存放小节
        for idx,line in enumerate(md_line_list): # 进来的是每一行
            # 先去空格再说
            line = line.strip()
            # 先匹配代码块
            code_match = code_pattern.match(line)
            if code_match: # 匹配到代码块 看匹配到的是```还是~~~
                if code_block_before:  # 前面已经出现过~~~或者```
                    if code_match == marker: # 匹配到和之前一样的
                        code_block_before = False
                        marker = None
                        logger.info('代码块完结')
                else: # 前面没有```或者~~~
                    code_block_before = True
                    marker = code_match # 拿到匹配到的
            title_match = title_pattern.match(line)
            if code_block_before ==  False and title_match: # 没出现过```~~~且有标题符号
                pre_con_list = md_line_list[pre_idx:idx]  # 前文列表
                pre_con = '\n'.join(pre_con_list)  # 合成前文
                section = {
                    'file_title' : file_title,
                    'sec_title': pre_con_list[0] if pre_con_list[0].startswith('#') else '无题',
                    'sec_con': pre_con,
                }
                pre_idx = idx
                sec_list.append(section)
        # 剩最后一段
        sec_list.append({
            'file_title' : file_title,
            'sec_title': md_line_list[pre_idx],
            'sec_con': '\n'.join(md_line_list[pre_idx:]),
        })
        # 精切 这时候我拥有一个充满小节的列表
        chunk_size =1000
        chunk_overlap = 50
        spliter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],
        )
        # 先取头再切  他妈遍历的时候别几把动原列表 迭代器会几把失效  用个新列表装
        final_sec_list = []
        for sec in sec_list:
            sec_con = sec.get('sec_con', '')
            sec_title = sec.get('sec_title', '')
            # starswith可以对字符串使用
            real_con = sec_con[len(sec_title):] if sec_con.startswith('#') else sec_con
            # 太短 有表格  就不切(还是要加到列表里) 特殊情况if 或者if not解决
            if len(real_con) < chunk_size:
                final_sec_list.append({
                    **sec,
                    'part' :0 , # 第几部分:没切的部分
                })
                continue
            if '<table' in real_con:
                final_sec_list.append({
                    **sec,
                    'part' :0 , # 第几部分:没切的部分
                })
                continue
            # 其他全几把切了
            chunk_list = spliter.split_text(real_con)  # 可能不止一个
            for idx,chunk in enumerate(chunk_list):
                final_sec_list.append({
                    'file_title': file_title,
                    'sec_title': sec_title,
                    'sec_con': sec_title + '\n' + chunk,
                    'part': idx,
                })

            # 搞完备份一个json
            json_path = md_path_obj.parent /  'chunk.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_format(final_sec_list))



if __name__ == '__main__':
    node = node_content_split()
    init_state = {
        'md_path': r'D:\kb_pro_imitation\output\万用表RS-12的使用\万用表RS-12的使用_new.md',
    }
    res = node(init_state)

