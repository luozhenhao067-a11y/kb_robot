# 单例
import json
import os
from minio import Minio
from tool.logger import logger

minio_client = None

def get_minio_client():
    global minio_client
    print(f"哈哈哈哈哈我他妈被调用了, minio_client = {minio_client}")
    try:
        if not minio_client:

            minio_client = Minio(
                endpoint = os.getenv("MINIO_ENDPOINT"),
                access_key = os.getenv("MINIO_ACCESS_KEY"),
                secret_key = os.getenv("MINIO_SECRET_KEY"),
                # 禁用https 必须他妈的加
                secure = False,
            )

            bucket_name = os.getenv("MINIO_BUCKET_NAME")
            # 创建bucket
            if not minio_client.bucket_exists(bucket_name = bucket_name):
                minio_client.make_bucket(bucket_name = bucket_name)

            # 桶权限
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": f"arn:aws:s3:::{bucket_name}",
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    },
                ],
            }
            minio_client.set_bucket_policy(bucket_name=bucket_name, policy=json.dumps(policy))
    except Exception as e:
        # except
        logger.error(f'妈的连不上啊,{e}')
        raise Exception('妈的连不上啊')
    return minio_client


if __name__ == '__main__':
    get_minio_client()

