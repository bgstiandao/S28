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

    #解决跨域（设置）
    cors_config = {
        'CORSRule':[
            {
                'AllowedOrigin':'*',	#['http://www.qq.com','http://www.xxx.com']
                'AllowedMethod':['GET','PUT','HEAD','POST','DELETE'],
                'AllowedHeader':'*',	#['x-cos-meta-test']
                'ExposeHeader':'*',	#['x-cos-meta-test']
                'MaxAgeSeconds':500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
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


def delete_file(bucket, region,key):
    config = CosConfig(Region=region,SecretKey=settings.TENCENT_COS_ID, SecretId=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key
    )


def delete_file_list(bucket, region,key_list):
    config = CosConfig(Region=region,SecretKey=settings.TENCENT_COS_ID, SecretId=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 批量删除文件
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )

def credential(bucket, region):
    """获取cos上传临时凭证"""
    # 生成一个临时凭证，并给前端返回
    # 1.安装一个生成临时凭证python模块		pip install -U qcloud-python-sts
    # 2.写代码
    from sts.sts import Sts
    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 1800,
        # 固定密钥id
        'secret_id': settings.TENCENT_COS_ID,
        # 固定密钥key
        'secret_key': settings.TENCENT_COS_KEY,
        # 换成你的bucket
        'bucket': bucket,
        # 换成bucker所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * （使用通配符*存在重大安全风险，请谨慎评估使用）
        'allow_prefix':'*',
        #密钥的权限列表，简单上传和分片需要以下的权限，其他权限请看https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 'name/cos:PutObject',
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # 'name/cos:UploadPart',
            # 'name/cos:UploadPartCopy',
            # 'name/cos:CompleteMultipartUpload',
            # 'name/cos:AbortMultipartUpload',
            "*",
        ],

    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict