# monkey_patch.py
"""
针对 qcloudsms_py 等旧库的 JSON 解码兼容性补丁。
将此文件导入到 Django 的启动设置中即可生效。
"""
import json
import sys

def safe_json_loads(s, *args, **kwargs):
    """
    一个安全的 json.loads 封装，会自动移除不被支持的 `encoding` 参数。
    """
    # 关键：移除可能引发 TypeError 的 'encoding' 参数
    kwargs.pop('encoding', None)
    # 调用原始的 json.loads 并返回结果
    return _original_json_loads(s, *args, **kwargs)

def apply_json_patch():
    """
    应用补丁到 json 模块。
    """
    global _original_json_loads
    # 保存原始函数
    _original_json_loads = json.loads
    # 用我们的安全版本替换它
    json.loads = safe_json_loads
    print("[Monkey Patch] 已成功替换 json.loads 以兼容旧版 SDK。")

# 可选：如果你想在导入此模块时自动应用补丁，可以取消下面这行的注释
# apply_json_patch()