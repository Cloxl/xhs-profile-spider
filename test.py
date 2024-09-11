import json

import execjs
import requests

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "x-b3-traceid": "0c9458dc7b3b25eb",
    "x-s-common": "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"
}
# TODO: 这里填入浏览器登录状态的cookie
cookies = {
    "a1": "",
    "web_session": "",
}
url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
data = {
    "keyword": "小红书网页版",
    "page": 1,
    "page_size": 20,
    "search_id": "2dqxbhgj7bscmr3qi5k81",
    "sort": "general",
    "note_type": 0,
    "ext_flags": [],
    "image_formats": [
        "jpg",
        "webp",
        "avif"
    ]
}

with open('./static/xs.js', 'r', encoding='utf-8') as f:
    xsxt = execjs.compile(f.read()).call(
        "get_xsxt", '/api/sns/web/v1/search/notes', data, cookies['a1']
    )

    headers['x-s'] = xsxt['X-s']
    headers['x-t'] = str(xsxt['X-t'])

# xsc并不检测 如果需要可以放开这里的注释
# with open('static/xs_common.js', 'r', encoding='utf-8') as f:
#     js_code = f.read()
#     js_compiler = execjs.compile(js_code)
#
#     X_s_common = js_compiler.call(
#         "get_x_s_common",
#         headers['x-s'],
#         headers['x-t'],
#         48,
#         "I38rHdgsjopgIvesdVwgIC+oIELmBZ5e3VwXLgFTIxS3bqwErFeexd0ekncAzMFYnqthIhJeSBMDKutRI3KsYorWHPtGrbV0P9WfIi/eWc6eYqtyQApPI37ekmR1QL+5Ii6sdnoeSfqYHqwl2qt5B0DoIx+PGDi/sVtkIxdsxuwr4qtiIkrwIi/skcc3I3VvIC7sYuwXq9qtpFveDSJsSPwXIEvsiVtJOPw8BuwfPpdeTDWOIx4VIiu1ZPwbPutXIvlaLb/s3qtxIxes1VwHIkumIkIyejgsY/WTge7eSqte/D7sDcpipedeYrDtIC6eDVw2IENsSqtlnlSuNjVtIvoekqwMgbOe1eY2IESPIhhgQdIUI38P4mzgIiifpVwAICGVJo3sWm5s1uwlIvAe0dOeddpJIive3SWS2qwjIkKe3/ve1Z/siut4//OsjqwCIvTsaa6edVwupnesSqwmI3McI3mVouwwaVw+m0kKyb/sds6sVqwnIhAsjgee3WETIhgejIveVUhdIi0e3Pw6IkqAtuweOqwDICOsiVwSIhgsiqwlIh/eDqtAHqwPmVwDIvquIxI/Gfij2c/exqtAIhi4IkJeSPwarm+4pUdsYsQ1IiqrqqtzZPwXIvdexqtSPFJeTzAsVLRbIhKsVdesiVtapuwNIveejuwuIigeT0hbIvAejfKeSutMIx3s6Pwx8glPIEZqIvOs6p6ex7vsYD7sdutzIkL1IvPYnqwnIxQCI3As3bHvNjOs0uteIEb+ZqtRyZosjMAeWVwbsuwgIC8MIiZQnuw4yutgIieeWlvexuwKpqw2IizZcut1Iv8Qzs4ZIEAe0agedjesVutJyVwQIERBICNexuwRIiosfmLYICLs/DWmI3WQI3gsTqwABqw+GuwuIvHrIvOe1aZ=",
#         cookies['a1']
#     )
#     headers['x-s-common'] = X_s_common
#     headers['x_b3_traceid'] = js_compiler.call("x_b3_traceid")

response = requests.post(url, headers=headers, cookies=cookies,
                         data=json.dumps(data, separators=(',', ':'), ensure_ascii=False))

print(response.text)
