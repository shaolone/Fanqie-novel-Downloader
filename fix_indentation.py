#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复settings.py中的缩进问题
"""

import re

def fix_indentation():
    with open('settings.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式修复缩进问题
    fixed_content = re.sub(
        r'if category in CONFIG:\s+CONFIG\[category\]\.update',
        r'if category in CONFIG:\n                CONFIG[category].update',
        content
    )
    
    # 保存修复后的文件
    with open('settings.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("settings.py 文件的缩进问题已修复！")

if __name__ == "__main__":
    fix_indentation() 