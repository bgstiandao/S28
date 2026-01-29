import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)       #把当前的根目录导入到sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'S28.settings')
django.setup()      #读取os.environ[DJANGO_SETTINGS_MODULE]

from web import models      #必须是django.setup()之后才能导入

#往数据库添加数据：链接数据库，操作，关闭链接
models.UserInfo.objects.create(username='焱垚', email='1234567@qq.com',mobile_phone='15323422342', password='123456789')

