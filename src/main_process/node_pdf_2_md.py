import json
import time
from pathlib import Path
from typing import Any

from config.config import MinerUConfig
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.json_format import json_format
from tool.logger import logger



class node_pdf_2_md(NodeBase):
    name = 'node_pdf_2_md'
    def process(self,state: ImportGraphState):
        # 进来先防御编程
        local_dir_obj, pdf_path, pdf_path_obj = self.check_file(state)
        #  mineru 操作 传文件 收文件环节
        batch_id = self.upload_pdf(pdf_path, pdf_path_obj)
        # 上传完请求结果
        requests, zip_url = self.ask_4_zip(batch_id)
        # 拿到压缩包地址         下载&解压&重命名
        # 下载也是请求
        md_content, new_path = self.download_and_fucking_unzip(local_dir_obj, pdf_path_obj, requests, zip_url)
        return {
            'md_path': str(new_path),
            'md_content': md_content,
        }

    def download_and_fucking_unzip(self, local_dir_obj: Path, pdf_path_obj: Path, requests, zip_url) -> tuple[Path, str]:
        zip_url_res = requests.get(zip_url)
        if zip_url_res.status_code != 200:
            logger.info('他妈请求都不成功 回家吧')
            raise Exception('他妈请求都不成功 回家吧')
        # 这个返回体结构不一样 所以不是三次 这是拿到文件的二进制内容
        md_zip_content = zip_url_res.content
        # 构造磁盘文件地址
        md_zip_path_obj = local_dir_obj / f"{pdf_path_obj.stem}.zip"
        # 写入磁盘
        with open(md_zip_path_obj, 'wb') as f:
            f.write(md_zip_content)

        # 解压这个obj
        import zipfile

        # 这是拿到Zipfile对象而已
        zip_file_content = zipfile.ZipFile(md_zip_path_obj)
        # 准备存放路径(只要是路径  都要完整) 这是path对象
        zip_file_path = local_dir_obj / f"{pdf_path_obj.stem}"
        # 解压文件
        if zip_file_path.exists():
            logger.info('他妈的这个目录已经存在了 删除他')
            import shutil
            shutil.rmtree(zip_file_path)
        logger.info('没文件 我帮你创建一个')
        zip_file_path.mkdir()
        # 解压
        zip_file_content.extractall(zip_file_path)

        # 解压的默认的md名字叫full.md 改个好听的名字
        md_file_origin_obj = zip_file_path / "full.md"
        new_path =md_file_origin_obj.with_name(f"{pdf_path_obj.stem}.md")
        # 落盘
        md_file_origin_obj.rename(new_path)
        logger.info('他妈的md文件已经生成了 快去读吧')
        with open(new_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        return md_content, new_path

    def ask_4_zip(self, batch_id) -> tuple[Any, Any]:
        import requests

        token = MinerUConfig.mineru_token
        batch_id = batch_id
        url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        time_limit = 300
        sum_time = 0
        while sum_time < time_limit:
            start_time = time.time()
            res = requests.get(url, headers=header)
            try:
                if res.status_code != 200:
                    logger.info('他妈请求都不成功 回家吧')
                    raise Exception('他妈请求都不成功 回家吧')
                res = res.json()
                if res['code'] != 0:
                    logger.info('他妈数据都不给 回家吧')
                    raise Exception('他妈数据都不给 回家吧')
                logger.info('数据给成功  看看他给了个啥玩意')
                data = res['data']['extract_result'][0]
                if data['state'] != 'done':
                    logger.info('他妈数据还没准备好 稍等')
                    raise Exception('他妈数据还没准备好 稍等')
                logger.info(f'哈哈数据都准备好了  这下稳了,时间{sum_time}')
                zip_url = data['full_zip_url']
                return requests, zip_url
            except Exception as e:
                logger.info(f'请求只因了  看看原因吧:{e}')
                end_time = time.time()
                sum_time += (end_time - start_time)
                if sum_time >= time_limit:
                    logger.info('这么就都获取不了数据 滚回家吧')
                    raise Exception('这么就都获取不了数据 滚回家吧')
                time.sleep(1)
                continue
            end_time = time.time()
            sum_time += (end_time - start_time)


    def upload_pdf(self, pdf_path: str, pdf_path_obj: Path) -> Any:
        import requests

        token = MinerUConfig.mineru_token
        url = "https://mineru.net/api/v4/file-urls/batch"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "files": [
                # .name 是带后缀的
                {"name": f"{pdf_path_obj.name}", "data_id": "abcd"}
            ],
            "model_version": "vlm"
        }
        # 人家要的是字符串 Path是一个工具箱
        file_path = [f"{pdf_path}"]
        # 三层判断
        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            logger.info('他妈请求都不成功 回家吧')
            raise Exception('他妈请求都不成功 回家吧')
        logger.info('请求成功 看看数据人家给不给')
        res = response.json()
        if res['code'] != 0:
            logger.info('他妈数据都不给 回家吧')
            raise Exception('他妈数据都不给 回家吧')
        logger.info('数据给成功 拿id和url')
        batch_id = res['data']['batch_id']
        urls = res['data']['file_urls']
        for i in range(0, len(urls)):
            with open(file_path[i], 'rb') as f:
                res_upload = requests.put(urls[i], data=f)
                if res_upload.status_code == 200:
                    logger.info(f"{urls[i]} 上传他妈的成功")
                else:
                    print(f"{urls[i]} 上传他妈的失败")
        return batch_id

    def check_file(self, state: ImportGraphState) -> tuple[Path, str, Path]:
        pdf_path = state.get('pdf_path', '')
        if not pdf_path:
            logger.info('他妈的PDF路径都没有啊,诗人???')
            raise Exception('他妈的PDF路径都没有啊,诗人???')
        logger.info('PDF路径倒是有 我看看你小子有没有放文件')
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            logger.info('PDF路径里没有文件啊???')
            raise Exception('PDF路径里没有文件啊???')
        logger.info('PDF路径里文件有 搞个输出目录先,别急')
        local_dir = state.get('local_dir', '')
        if not local_dir:
            logger.info('他妈的输出目录都没有啊,诗人??? 算了,帮你小子创一个')
            # 创建文件的逻辑是先路径  然后mkdir
            local_dir = Path(r'D:\kb_pro_imitation\output')
        logger.info('输出目录倒是有 我看看你小子有没有放文件夹')
        local_dir_obj = Path(local_dir)
        # .exist是检查最后一个文件有没有
        if not local_dir_obj.exists():
            logger.info('输出目录里没有文件夹啊???算了 ,帮你创一个吧')
            # 递归是逐级创建  不递归只创建最后一个文件夹
            local_dir_obj.mkdir(parents=True, exist_ok=True)
        return local_dir_obj, pdf_path, pdf_path_obj



if __name__ == '__main__':
    node_tran = node_pdf_2_md()
    init_state = {
        'pdf_path': r'D:\kb_pro_imitation\05-device_txt\doc\万用表RS-12的使用.pdf',
    }
    res = node_tran(init_state)
    res = json_format(res)
    logger.info(f"拿到结果了 是{res}")










