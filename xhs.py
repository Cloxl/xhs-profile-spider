import json
import os
import random
import re
import time
from datetime import datetime
from io import BytesIO
from typing import Any

import execjs
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from PIL import Image

from EncryptHelper import EncryptHelper

cookies = {
    "a1": "",
    "web_session": "",
}
user_id = ""
target_like_count = 100
formatter_type = "评论数量"

tmp_json_path = './tmp.json'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://www.xiaohongshu.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.xiaohongshu.com/',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
}
if not user_id:
    logger.error("未提取到用户id 无法进行下一步检索!")
    exit(10086)
if formatter_type not in ["点赞数量", "收藏数量", "分享数量", "评论数量"]:
    logger.error(f"错误: 排序字段 '{formatter_type}' 无效")
    exit(10087)

# 处理获取index.html的数据
url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
session = requests.Session()
response = session.get(url, headers=headers, cookies=cookies)


# 处理index.html中的js数据
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

        # 使用JavaScript文件进行格式化解析
        with open('./static/formatJson.js', 'r', encoding='utf-8') as js_file:
            execjs.compile(js_file.read()).call('get_jc', extracted_content)

        # 将解析后的内容保存为JSON文件
        with open(output_json_path, 'r', encoding='utf-8') as output_file:
            return json.loads(output_file.read())

    else:
        # 未找到 window.__INITIAL_STATE__ 的情况
        logger.error("未找到 window.__INITIAL_STATE__")
        return None


# 简单的重试机制
def fetch(url: str) -> Any | None:
    while True:
        resp = session.get(url, headers=headers, cookies=cookies)

        if resp.status_code != 200:
            if resp.status_code == 461:
                logger.warning("出现验证码 请前往小红书网页端随意滑动过掉验证码再使用本脚本!\n输入0跳过当前请求")

                user_input = input("请输入选项: ")
                if user_input.strip() == '':  # 检查空输入
                    continue  # 跳过当前请求

                try:
                    if int(user_input) == 0:
                        return None  # 跳出当前请求
                except ValueError:
                    logger.warning("输入无效，继续重试当前请求...")
                    continue  # 跳过当前请求

            else:
                logger.error(f"状态码: {resp.status_code}, 内容: {resp.text}")
                logger.error("数据爬取失败! 退出本次爬取, 当前内容已生成在output.xlsx")
                return None  # 请求失败退出函数
        else:
            return resp


if user_profile_data := extract_initial_state(response.text, tmp_json_path):
    user_profile_data = user_profile_data['user']['notes'][0]

rows = []
for fetch_profile_data in user_profile_data:
    note_card = fetch_profile_data["noteCard"]
    row = {
        "笔记标题": note_card.get("displayTitle", ""),

        "点赞数量": note_card['interactInfo'].get("likedCount", ""),
        "收藏数量": note_card['interactInfo'].get("collectedCount", 0),
        "分享数量": note_card['interactInfo'].get("shareCount", 0),
        "评论数量": note_card['interactInfo'].get("commentCount", 0),

        "内容形式": "图文" if note_card.get("type") == "normal" else "视频"
        if note_card.get("type") == "video" else note_card.get("type", ""),

        "用户昵称": note_card['user'].get("nickname", ""),
        "笔记ID": fetch_profile_data.get("id", ""),
        "笔记链接": f"https://www.xiaohongshu.com/explore/{fetch_profile_data['id']}?xsec_token{fetch_profile_data['xsecToken']}"
    }
    rows.append(row)

if not rows:
    logger.error("首次爬取未获取到用户的任何内容")
    exit(10088)

# 处理后续的笔记链接
while True:
    host = "https://edith.xiaohongshu.com"
    url = "/api/sns/web/v1/user_posted"
    params = {
        "num": "30",
        "cursor": rows[-1]['笔记ID'],
        "user_id": user_id,
        "image_formats": "jpg,webp,avif"
    }

    c = f'{url}?{"&".join([f"{key}={value}" for key, value in params.items()])}'
    #如果需求为post
    #data = json.dumps(params, separators=(", ", ": "), ensure_ascii=False)
    #c = f'{url}{data}'
    t = str(round(int(time.time()) * 1000))
    xs = EncryptHelper.encrypt_xs(url=c, a1=cookies["a1"], ts=t)
    headers['x-s'], headers['x-t'] = xs, t

    # xsc并不检测 如果需要可以放开这里的注释
    with open('static/xs_common.js', 'r', encoding='utf-8') as f:
        js_code = f.read()
        js_compiler = execjs.compile(js_code)

        X_s_common = js_compiler.call(
            "get_x_s_common",
            headers['x-s'],
            headers['x-t'],
            48,
            "I38rHdgsjopgIvesdVwgIC+oIELmBZ5e3VwXLgFTIxS3bqwErFeexd0ekncAzMFYnqthIhJeSBMDKutRI3KsYorWHPtGrbV0P9WfIi/eWc6eYqtyQApPI37ekmR1QL+5Ii6sdnoeSfqYHqwl2qt5B0DoIx+PGDi/sVtkIxdsxuwr4qtiIkrwIi/skcc3I3VvIC7sYuwXq9qtpFveDSJsSPwXIEvsiVtJOPw8BuwfPpdeTDWOIx4VIiu1ZPwbPutXIvlaLb/s3qtxIxes1VwHIkumIkIyejgsY/WTge7eSqte/D7sDcpipedeYrDtIC6eDVw2IENsSqtlnlSuNjVtIvoekqwMgbOe1eY2IESPIhhgQdIUI38P4mzgIiifpVwAICGVJo3sWm5s1uwlIvAe0dOeddpJIive3SWS2qwjIkKe3/ve1Z/siut4//OsjqwCIvTsaa6edVwupnesSqwmI3McI3mVouwwaVw+m0kKyb/sds6sVqwnIhAsjgee3WETIhgejIveVUhdIi0e3Pw6IkqAtuweOqwDICOsiVwSIhgsiqwlIh/eDqtAHqwPmVwDIvquIxI/Gfij2c/exqtAIhi4IkJeSPwarm+4pUdsYsQ1IiqrqqtzZPwXIvdexqtSPFJeTzAsVLRbIhKsVdesiVtapuwNIveejuwuIigeT0hbIvAejfKeSutMIx3s6Pwx8glPIEZqIvOs6p6ex7vsYD7sdutzIkL1IvPYnqwnIxQCI3As3bHvNjOs0uteIEb+ZqtRyZosjMAeWVwbsuwgIC8MIiZQnuw4yutgIieeWlvexuwKpqw2IizZcut1Iv8Qzs4ZIEAe0agedjesVutJyVwQIERBICNexuwRIiosfmLYICLs/DWmI3WQI3gsTqwABqw+GuwuIvHrIvOe1aZ=",
            cookies['a1']
        )
        headers['x-s-common'] = X_s_common
        headers['x_b3_traceid'] = js_compiler.call("x_b3_traceid")

    response = fetch(host+c)
    if not response.json()['data']:
        logger.error(f"网页请求成功 但是提取数据发生错误 终止请求 当前内容已生成在output.xlsx")
        break

    data = response.json()["data"]["notes"]
    has_more = response.json()["data"]["has_more"]
    for fetch_profile_data in data:
        row = {
            "笔记标题": fetch_profile_data.get("display_title", ""),

            "点赞数量": fetch_profile_data['interact_info'].get("liked_count", ""),
            "收藏数量": fetch_profile_data['interact_info'].get("collectedCount", 0),
            "分享数量": fetch_profile_data['interact_info'].get("shareCount", 0),
            "评论数量": fetch_profile_data['interact_info'].get("commentCount", 0),

            "内容形式": "图文" if fetch_profile_data.get("type") == "normal" else "视频"
            if fetch_profile_data.get("type") == "video" else fetch_profile_data.get("type", ""),

            "用户昵称": fetch_profile_data['user'].get("nickname", ""),
            "笔记ID": fetch_profile_data['note_id'],
            "笔记链接": f"https://www.xiaohongshu.com/explore/{fetch_profile_data['note_id']}?xsec_token{fetch_profile_data['xsec_token']}"
        }
        rows.append(row)

    if not has_more:
        logger.success("数据爬取完毕")
        break

    sleeper_time = random.randint(4, 10)
    logger.success(f"单次数据爬取成功, 延时{sleeper_time}秒后继续爬取")
    time.sleep(sleeper_time)


# 对点赞数量大于指定内容的笔记获取更多数据 并进行下载
pre_path = f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
for row in rows:
    if int(row['点赞数量']) < target_like_count:
        continue

    response = fetch(row['笔记链接'])
    if not response:
        logger.warning(f"网页请求失败 当前文章: {row['笔记ID']}")
        continue

    user_note_data = extract_initial_state(html_content=response.text, output_json_path=tmp_json_path)

    if not user_note_data:
        logger.warning(f"网页请求成功 但是提取数据发生错误 跳过当前文章 {row['笔记ID']}")
        continue

    try:
        user_note_info = user_note_data['note']['noteDetailMap'][row['笔记ID']]['note']
        row['收藏数量'] = user_note_info['interactInfo'].get('collectedCount', 0)
        row['分享数量'] = user_note_info['interactInfo'].get('shareCount', 0)
        row['评论数量'] = user_note_info['interactInfo'].get('commentCount', 0)
    except KeyError:
        logger.warning("小红书返回了空的数据 具体问题还在排查中 \n 相关数据保存在output.xlsx \n 退出程序")
        break

    pre_path += f"/{row['笔记ID']}"
    os.makedirs(pre_path, exist_ok=True)

    # 获取文章内容row['笔记ID']
    with open(f"{pre_path}/content.txt", "w", encoding="utf-8") as f:
        f.write(row['笔记标题'] + '\n\n' + user_note_info['desc'])

    # 下载webp图片使用pil转为jpg
    for i, img_urls in enumerate(user_note_info['imageList']):
        img_url = img_urls['urlDefault']

        response = requests.get(img_url, headers=headers)
        byte_stream = BytesIO(response.content)
        im = Image.open(byte_stream)

        if im.mode == "RGBA":
            im.load()
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])

        im.save(f"{pre_path}/{i}.jpg", 'JPEG')

    sleeper_time = random.randint(3, 10)
    logger.success(f"单次文章爬取成功, 延时{sleeper_time}秒后继续爬取")
    time.sleep(sleeper_time)

try:
    rows = sorted(rows, key=lambda x: int(x[formatter_type]), reverse=True)
except ValueError:
    logger.error(f"排序时出现问题，请确认字段 {formatter_type} 是否存在并且是可以转换为整数的内容")
    exit(10089)

df = pd.DataFrame(rows)
df.to_excel('output.xlsx', index=False)
