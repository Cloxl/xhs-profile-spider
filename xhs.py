import json
import random
import re
import time

import execjs
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

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
cookies = {
    "a1": "",
    "web_session": "",
}
url = "https://www.xiaohongshu.com/user/profile/{}".format("ewg")

response = requests.get(url, headers=headers, cookies=cookies)


soup = BeautifulSoup(response.text, 'html.parser')
script_tags = soup.find_all('script')
pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*({.*})', re.DOTALL)


initial_state_str = None
for script_tag in script_tags:
    if script_tag.string and 'window.__INITIAL_STATE__' in script_tag.string:
        match = pattern.search(script_tag.string)
        if match:
            initial_state_str = match.group(1)
            break

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
else:
    print("未找到 window.__INITIAL_STATE__")
    print(response.text)
    exit(10086)


with open('./static/formatJson.js', 'r', encoding='utf-8') as f:
    jx = execjs.compile(f.read()).call(
        'get_jc', extracted_content
    )

with open('./test.json', 'r', encoding='utf-8') as f:
    rows = []
    jc = json.loads(f.read())['user']
    data = jc['notes'][0]
    user_id = jc['noteQueries'][0].get('userId', "")


for result in data:
    note_card = result["noteCard"]
    row = {
        "笔记标题": note_card.get("displayTitle", ""),
        "点赞数量": note_card['interactInfo'].get("likedCount", ""),
        "内容形式": "图文" if note_card.get("type") == "normal" else "视频"
        if note_card.get("type") == "video" else note_card.get("type", ""),

        "用户昵称": note_card['user'].get("nickname", ""),
        "笔记ID": result.get("id", ""),
        "笔记链接": f"https://www.xiaohongshu.com/explore/{result['id']}?xsec_token{result['xsecToken']}"
    }
    rows.append(row)

if not user_id:
    logger.error("未提取到用户id 无法进行下一步检索!")

    df = pd.DataFrame(rows)
    df.to_excel('output.xlsx', index=False)

    exit(10086)

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

    response = requests.get(url=host+c, headers=headers, cookies=cookies)

    if not response.json()['data']:
        logger.error("数据爬取失败!")
        logger.error(f"状态码: {response.status_code}, 内容: {response.text}")
        break

    data = response.json()["data"]["notes"]
    has_more = response.json()["data"]["has_more"]
    for result in data:
        row = {
            "笔记标题": result.get("display_title", ""),
            "点赞数量": result['interact_info'].get("liked_count", ""),
            "内容形式": "图文" if result.get("type") == "normal" else "视频"
            if result.get("type") == "video" else result.get("type", ""),

            "用户昵称": result['user'].get("nickname", ""),
            "笔记ID": result['note_id'],
            "笔记链接": f"https://www.xiaohongshu.com/explore/{result['note_id']}?xsec_token{result['xsec_token']}"
        }
        rows.append(row)

    if not has_more:
        logger.success("数据爬取完毕")
        break

    sleeper_time = random.randint(4, 10)
    logger.success(f"单次数据爬取成功, 延时{sleeper_time}秒后继续爬取")
    time.sleep(sleeper_time)

df = pd.DataFrame(rows)
df.to_excel('output.xlsx', index=False)
