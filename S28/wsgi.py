"""
WSGI config for S28 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# +++ 新增补丁代码开始 +++
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) # 确保能找到补丁文件
try:
    from monkey_patch import apply_json_patch
    apply_json_patch()
except ImportError:
    print("警告：未找到 monkey_patch.py，JSON 兼容性补丁未应用。")
# +++ 新增补丁代码结束 +++

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'S28.settings')

application = get_wsgi_application()
