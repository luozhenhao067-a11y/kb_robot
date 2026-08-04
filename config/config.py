import os
from dotenv import load_dotenv
# 记住要重写
load_dotenv(override= True)

class MinerUConfig:
    mineru_token = os.getenv("MINERU_TOKEN")


class ALI_config:
    ali_api_key = os.getenv("ALI_API_KEY")
    ali_base_url = os.getenv("ALI_BASE_URL")
    vl_name = os.getenv("VL_NAME")


class minio_config:
    minio_endpoint = os.getenv("MINIO_ENDPOINT")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")
    minio_img_dir = os.getenv("MINIO_IMG_DIR")

