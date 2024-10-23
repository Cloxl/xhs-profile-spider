import json
import re
from typing import Any

import execjs
from bs4 import BeautifulSoup
from loguru import logger


def extract_initial_state(html_content: str, output_json_path: str) -> Any | None:
    """
    从HTML中的<script>标签中提取window.__INITIAL_STATE__ 解析并保存为JSON格式

    如果未找到 window.__INITIAL_STATE__ 函数会返回 None 并输出响应的HTML内容
    :param html_content: str html文档内容
    :param output_json_path: str 输出保存JSON的文件路径

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

    # 找到初始状态字符串
    if initial_state_str:
        stack = []
        result = []

        # 解析大括号 {} 来提取内容
        for char in initial_state_str:
            if char == '{':
                stack.append('{')
            elif char == '}':
                stack.pop()

            result.append(char)

            if not stack:
                break

        extracted_content = ''.join(result)

        # html提取的内容为js obj需要通过js序列化
        with open('./static/formatJson.js', 'r', encoding='utf-8') as js_file:
            return json.loads(execjs.compile(js_file.read()).call('get_jc', extracted_content))

    else:
        # 如果未找到, 说明请求出问题 可能账户被特征了
        logger.error("未找到 window.__INITIAL_STATE__")
        return None
