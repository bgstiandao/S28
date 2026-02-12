import mimetypes
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

def upload_file(bucket, region,file_object,key):
    # 文件对象上传到当前项目的桶中
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)

    # 2.获取客户端对象
    client = CosS3Client(config)

    # 自动获取文件的 MIME 类型
    content_type = mimetypes.guess_type(key)[0] or 'application/octet-stream'

    # 3.上传文件
    # response = client.upload_file(
    #     Bucket=request.tracer.project.bucket,
    #     LocalFilePath='code.png',  # 本地文件的路径
    #     Key='p1.png',  # 上传到桶之后的文件名
    # )

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key,  # 上传到桶之后的文件名
        ContentType=content_type,   #图片响应形式
        ContentDisposition='inline',    #强制浏览器内显示
    )

    # https: // pypu - 18309280693 - 1770822331803 - 1392471131. cos.ap - shanghai.myqcloud.com / 5fa46718f14b430f281ede063e256b57.png

    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)
