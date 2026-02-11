from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

def create_bucket(bucket,region='ap-shanghai'):
    """
    创建桶
    :param bucket:桶名称
    :param region:区域
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)

    # 2.获取客户端对象
    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read',  # private  / public-read  / public-read-write
    )
