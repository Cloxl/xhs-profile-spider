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

cookies = {
    "a1": "",
    "web_session": "",
}
user_id = ""
target_like_count = 100

tmp_json_path = './tmp.json'
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://www.xiaohongshu.com/explore",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
if not user_id:
    logger.error("未提取到用户id 无法进行下一步检索!")
    exit(10086)

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
for profile_data in user_profile_data:
    note_card = profile_data["noteCard"]
    row = {
        "笔记标题": note_card.get("displayTitle", ""),

        "点赞数量": note_card['interactInfo'].get("likedCount", ""),
        "收藏数量": note_card['interactInfo'].get("collectedCount", "未满足要求不爬取"),
        "分享数量": note_card['interactInfo'].get("shareCount", "未满足要求不爬取"),
        "评论数量": note_card['interactInfo'].get("commentCount", "未满足要求不爬取"),

        "内容形式": "图文" if note_card.get("type") == "normal" else "视频"
        if note_card.get("type") == "video" else note_card.get("type", ""),

        "用户昵称": note_card['user'].get("nickname", ""),
        "笔记ID": profile_data.get("id", ""),
        "笔记链接": f"https://www.xiaohongshu.com/explore/{profile_data['id']}?xsec_token{profile_data['xsecToken']}"
    }
    rows.append(row)

if not rows:
    logger.error("首次爬取未获取到用户的任何内容")
    exit(10086)

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

    with open('./static/xs.js', 'r', encoding='utf-8') as f:
        xsxt = execjs.compile(f.read()).call(
            "get_xsxt", c, "undefined", cookies['a1']
        )

        headers['x-s'] = xsxt['X-s']
        headers['x-t'] = str(xsxt['X-t'])

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
    for profile_data in data:
        row = {
            "笔记标题": profile_data.get("display_title", ""),
            "点赞数量": profile_data['interact_info'].get("liked_count", ""),
            "内容形式": "图文" if profile_data.get("type") == "normal" else "视频"
            if profile_data.get("type") == "video" else profile_data.get("type", ""),

            "用户昵称": profile_data['user'].get("nickname", ""),
            "笔记ID": profile_data['note_id'],
            "笔记链接": f"https://www.xiaohongshu.com/explore/{profile_data['note_id']}?xsec_token{profile_data['xsec_token']}"
        }
        rows.append(row)

    if not has_more:
        logger.success("数据爬取完毕")
        break

    sleeper_time = random.randint(4, 10)
    logger.success(f"单次数据爬取成功, 延时{sleeper_time}秒后继续爬取")
    time.sleep(sleeper_time)

# 排序 在excel文件中无需再次排序
rows = sorted(rows, key=lambda x: int(x["点赞数量"]), reverse=True)


# 对点赞数量大于指定内容的笔记获取更多数据 并进行下载
pre_path = f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
for row in rows:
    if int(row['点赞数量']) < target_like_count:
        break  # 经过排序 前面的项一定 >= target_like_count

    response = fetch(row['笔记链接'])
    if not response:
        logger.warning(f"网页请求失败 当前文章: {row['笔记ID']}")
        continue

    user_note_data = extract_initial_state(html_content=response.text, output_json_path=tmp_json_path)

    if not user_note_data:
        logger.warning(f"网页请求成功 但是提取数据发生错误 跳过当前文章 {row['笔记ID']}")
        continue

    user_note_info = user_note_data['note']['noteDetailMap'][row['笔记ID']]['note']
    row['收藏数量'] = user_note_info['interactInfo'].get('collectedCount', '获取异常')
    row['分享数量'] = user_note_info['interactInfo'].get('shareCount', '获取异常')
    row['评论数量'] = user_note_info['interactInfo'].get('commentCount', '获取异常')

    pre_path += f"/{row['笔记ID']}"
    os.makedirs(pre_path, exist_ok=True)

    # 获取文章内容
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

df = pd.DataFrame(rows)
df.to_excel('output.xlsx', index=False)
