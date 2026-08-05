import base64
import os
import re
import time
from collections import deque
from pathlib import Path
from typing import Any
from minio.deleteobjects import DeleteObject
from config.config import ALI_config,  minio_config
from langchain.chat_models import init_chat_model
from main_process.base import NodeBase
from main_process.state import ImportGraphState
from tool.logger import logger
from tool.minio_client import get_minio_client


class node_md_img(NodeBase):

    name = 'node_md_img'

    def process(self, state: ImportGraphState):
        # 1. 防御性编程 看有没有内容
        md_path_obj, md_content =self.check_file(state)
        #  文件里有内容 , 看看有没有存图片先
        image_dir_path_obj = md_path_obj.parent / 'images'
        if not image_dir_path_obj.exists():
            logger.info('他妈的md文件里没有图片啊???直接返回md内容了')
            return {
                'md_content': md_content,
            }
        image_name_list = os.listdir(image_dir_path_obj)
        if not image_name_list:
            logger.info('我去文件夹一个文件都没有啊???直接返回md内容了')
            return {
                'md_content': md_content,
            }
        # 2.什么都有 非常标准的格式 拿图片+上下文
        im_con_list = self.get_im_con(image_name_list, md_content, image_dir_path_obj)
        # 3.可以交大模型总结图片内容
        # 利用滑动门算法
        image_with_sum =  self.get_im_with_sum(im_con_list)
        # 4.把图片变成他妈的线上的
        # 先拿到客户端宝贝

        im_url_sum = self.get_im_url_sum(image_with_sum)
        # 5. 把原来的md改了  里面的图片是他妈的url懂?
        new_md_path = self.get_new_md(im_url_sum, md_content, md_path_obj)
        # 更新state 里面的路径
        return {
            'md_path' : new_md_path
        }

    def get_new_md(self, im_url_sum: list[Any], md_content: str, md_path_obj: Path) -> Path:
        for i in im_url_sum:
            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(i.get('image_name')) + r"\)")
            md_content = pattern.sub(lambda _: f'![{i.get('image_sum')}]({i.get('url')})', md_content)
        # 重新来一份md文件 懂?
        # 先地址 后写入
        new_md_path = md_path_obj.parent / str(md_path_obj.stem + '_new.md')
        with open(new_md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        return new_md_path

    def get_im_url_sum(self, image_with_sum: list[Any] | None) -> list[Any]:
        minio_client = get_minio_client()
        print('哈哈哈哈哈我他妈被调用了')
        # 再拿桶下面的文件夹啊
        upload_dir = minio_config.minio_img_dir
        # 盲清环境 1. 先拿 2. 后清
        old_image = minio_client.list_objects(
            bucket_name=minio_config.minio_bucket_name,
            #  去哪个文件夹里找文件
            prefix=upload_dir,
            recursive=True
        )
        # 把列表变成删除对象列表
        delete_object_list = [DeleteObject(i.object_name) for i in old_image]
        # 这他妈拿到的是一个生成器我操
        errors = minio_client.remove_objects(
            bucket_name=minio_config.minio_bucket_name,
            delete_object_list=delete_object_list,
        )
        # 遍历自动删除
        for error in errors:
            logger.error(f'删除图片失败:{error}')
        # 删完就把图片放上去
        # 同时有sum和url
        im_url_sum = []
        print(f"image_with_sum 长度: {len(image_with_sum)}")  # ← 加这行
        for i in image_with_sum:
            minio_client.fput_object(
                bucket_name=minio_config.minio_bucket_name,
                # 这里是除了桶之外的地址
                object_name=upload_dir + '/' + i.get('image_name'),
                file_path=i.get('image_path'),
            )
            logger.info(f'上传图片成功:{i.get("image_name")}')
            # 按照网站规则写url环节(并不是乱写的)
            url = f'http://{minio_config.minio_endpoint}/{minio_config.minio_bucket_name}/{minio_config.minio_img_dir}/{i.get("image_name")}'
            im_url_sum.append({
                **i,
                'url': url
            })
        return im_url_sum

    def check_file(self, state: ImportGraphState):
        md_path = state.get('md_path', '')
        # 字符串层面
        if not md_path:
            logger.info('他妈的md路径都没有啊,诗人???')
            raise Exception('他妈的md路径都没有啊,诗人???')
        # 物理层面
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            logger.info('他妈的md路径里没有文件啊???')
            raise Exception('他妈的md路径里没有文件啊???')
        #  文件里面有没有写内容
        with open(md_path_obj, 'r', encoding='utf-8') as f:
            md_content = f.read()
        if not md_content:
            logger.info('他妈的md文件里没有内容啊???')
            raise Exception('他妈的md文件里没有内容啊???')
        return md_path_obj, md_content

    def get_im_con(self, image_name_list, md_content, image_dir_path_obj):
        IMAGE_SUFFIX = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        CON_LEN = 500
        im_con_list = []
        for image_name in image_name_list:
            if not Path(image_name).suffix.lower() in IMAGE_SUFFIX:
                logger.info('处理不了,另谋高就')
                continue
            # 能处理  直接正则找

            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_name) + r"\)")

            get_pattern = pattern.search(md_content)
            print(get_pattern)
            # 找不到图片 一定要continue 不然第一张图片找不到就报错不走了
            if not get_pattern:
                logger.info('没有找到图片,另谋高就')
                continue
            # 通过正则得到开始和结束位置
            start, end = get_pattern.span()
            # 上文
            pre_txt = md_content[max(0, start - CON_LEN):start]
            # 下文
            post_txt = md_content[end:min(len(md_content), end + CON_LEN)]
            # 得到 图片名 图片路径 上文 下文
            im_con_list.append({
                'image_name': image_name,
                'image_path': str(image_dir_path_obj / image_name),
                'pre_txt': pre_txt,
                'post': post_txt,
            })
        return im_con_list

    def get_im_with_sum(self, im_con_list):
        dq = deque(maxlen=100)
        # 拿到当前时间戳 队列 里放的时间戳
        llm = init_chat_model(
            model=ALI_config.vl_name,
            model_provider='openai',
            api_key=ALI_config.ali_api_key,
            base_url=ALI_config.ali_base_url,
        )
        current_time = time.time()
        image_with_sum = []
        for image_con in im_con_list:
            # 先把过期的清理掉
            while dq and 60 - (current_time - dq[0]) <= 0:
                dq.popleft()
            # 满了
            if len(dq) == dq.maxlen:
                # 还有等待时间
                if 60 - (current_time - dq[0]) > 0:
                    # 关键行
                    time.sleep(60 - (current_time - dq[0]))
                    current_time = time.time()
                    while dq and 60 - (current_time - dq[0]) <= 0:
                        dq.popleft()
                # 无需等待了已经
                if 60 - (current_time - dq[0]) <= 0:
                    dq.popleft()
            # 没满直接添加
            dq.append(current_time)
            with open(image_con.get('image_path', ''), 'rb') as f:
                base64_str = base64.b64encode(f.read()).decode('utf-8')
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                # base64规定格式
                                "url": f"data:image/jpeg;base64,{base64_str}"
                            },
                        },
                        {"type": "text",
                         "text": f"""这是一张图片，图片上文部分为"{image_con.get("pre_txt")}"，
                                                 下文部分为"{image_con.get("post_txt")}"，
                                                 图片的名字是{image_con.get("image_name")},
                                                 请用中文简要总结这张图片的摘要,语言简洁优美,
                                                 字数在50字以内。"""},
                    ],
                },
            ]
            res = llm.invoke(messages)
            image_with_sum.append({
                'image_name': image_con.get('image_name'),
                'image_path': image_con.get('image_path'),
                'image_sum': res,
            })
            logger.info(f'给你看看总结结果得了{res}')
        return image_with_sum


if __name__ == '__main__':
    node = node_md_img()
    init_state = {
        'md_path': r'D:\kb_pro_imitation\output\万用表RS-12的使用\万用表RS-12的使用.md',
    }
    res = node(init_state)





