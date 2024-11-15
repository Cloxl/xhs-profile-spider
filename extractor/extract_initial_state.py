import asyncio
import json
import re
from typing import Any

from bs4 import BeautifulSoup
from loguru import logger


async def extract_initial_state(html_content: str, replacements: dict) -> dict | None:
    """
    从HTML中的<script>标签中提取window.__INITIAL_STATE__ 解析并保存为JSON格式

    如果未找到 window.__INITIAL_STATE__ 函数会返回 None 并输出响应的HTML内容
    :param html_content: html文档内容
    :param replacements: js对象转json需要替换的字符串对应关系

    :return: dict: 提取并格式化后的JSON数据
    """

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script')
    pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*({.*})', re.S)

    # 初始化初始状态字符串
    initial_state_str = None

    # 查找包含 "window.__INITIAL_STATE__" 的脚本标签
    for script_tag in script_tags:
        if script_tag.string and 'window.__INITIAL_STATE__' in script_tag.string:
            match = pattern.search(script_tag.string)
            if match:
                initial_state_str = match.group(1)
                break

    # 栈空间保证先入后出 可以确保提取所有的大括号
    # 具体原理查看 https://leetcode.cn/problems/valid-parentheses/description/
    if initial_state_str:
        stack = []
        result = []

        for char in initial_state_str:
            if char == '{':
                stack.append('{')
            elif char == '}':
                stack.pop()

            result.append(char)

            if not stack:
                break

        extracted_content = ''.join(result)

        for old, new in replacements.items():
            extracted_content = extracted_content.replace(old, new)

        return json.loads(extracted_content)
    else:
        # 如果未找到, 说明请求出问题 可能账户被特征了
        logger.error("未找到 window.__INITIAL_STATE__")
        return None
