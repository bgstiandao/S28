from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

secret_id = settings.TENCENT_COS_ID  # 用户的 SecretId
secret_key = settings.TENCENT_COS_KEY  # 用户的 SecretKey
region = 'ap-shanghai'  # 替换为用户的 region

token = None  # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)

# 2.获取客户端对象
client = CosS3Client(config)

# 3.上传文件
response = client.upload_file(
    Bucket='wangyang-1392471131',
    LocalFilePath='code.png',	 #本地文件的路径
    Key='p1.png',		#上传到桶之后的文件名

    # PartSize=1,       #默认参数，不用写
    # MAXThread=10,
    # EnableMD5=False
)
print(response['ETag'])