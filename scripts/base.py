"""离线脚本运行前导入的配置文件"""
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)       #把当前的根目录导入到sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'S28.settings')
django.setup()      #读取os.environ[DJANGO_SETTINGS_MODULE]