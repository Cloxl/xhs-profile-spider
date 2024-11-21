import asyncio
import base64
import json
import time
from asyncio import WindowsSelectorEventLoopPolicy
from code import XhsDesKeys
from code.captcha import CaptchaSolver
from typing import Dict, List

from pyDes import ECB, PAD_PKCS5, des

from encrypt import XsEncrypt
from xhs.request.AsyncRequestFramework import AsyncRequestFramework


class ProxyProvider:
    def __init__(self):
        self.arf = AsyncRequestFramework()

    async def get_proxies(self) -> List[str]:
        """获取代理IP列表

        Returns:
            List[str]: 代理IP列表
        """
        proxy_url = "http://bapi.51daili.com/getapi2"
        params = {
            "linePoolIndex": -1,
            "packid": 2,
            "time": 5,
            "qty": 100,
            "port": 1,
            "format": "txt",
            "sep": "\\n",
            "dt": 1,
            "ct": 1,
            "usertype": 17,
            "uid": 50940,
            "accessName": "",
            "accessPassword": ""
        }

        response = await self.arf.send_http_request(
            url=proxy_url,
            method="GET",
            params=params,
            back_fun=True,
            auto_sign=False
        )
        content = await response.acontent()
        proxy_list = content.decode().strip().split("\n")
        return proxy_list


class CaptchaService:
    def __init__(self):
        self.arf = AsyncRequestFramework()
        self.solver = CaptchaSolver()

    async def get_captcha_info(self, proxy: str = None) -> Dict:
        """获取验证码信息

        Args:
            proxy: 代理地址(可选)

        Returns:
            Dict: 验证码信息
        """
        url = "http://edith.xiaohongshu.com/api/redcaptcha/v2/captcha/register"
        payload = {
            "secretId": "000",
            "verifyType": "102",
            "verifyUuid": "",
            "verifyBiz": "461",
            "sourceSite": "",
            "captchaVersion": "1.3.0"
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.xiaohongshu.com',
            'referer': 'https://www.xiaohongshu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        ts = str(int(time.time() * 1000))
        headers['x-s'] = await XsEncrypt.encrypt_sign(
            ts=ts,
            payload=payload
        )
        headers['x-t'] = ts

        kwargs = {
            'url': url,
            'method': "POST",
            'json': payload,
            'headers': headers,
            'auto_sign': False
        }

        if proxy:
            kwargs['proxy'] = f"http://{proxy}"

        response = await self.arf.send_http_request(**kwargs)

        if not response:
            return {}

        captcha_info = json.loads(await self.solver.decrypt_data(
            encoded_data=response['data']['captchaInfo']
        ))

        bg_tag = captcha_info['backgroundUrl'].split('/')[-1].split('.')[0]

        return {
            bg_tag: [
                captcha_info['backgroundUrl'],
                captcha_info['captchaUrl']
            ]
        }


async def main(target_count: int = 100, use_proxy: bool = False) -> dict:
    """主函数

    Args:
        target_count: 目标请求数量
        use_proxy: 是否使用代理

    Returns:
        Dict: 验证码信息字典
    """
    captcha_service = CaptchaService()

    if use_proxy:
        proxy_provider = ProxyProvider()
        proxy_list = await proxy_provider.get_proxies()
        # 如果代理数量不够，循环使用
        while len(proxy_list) < target_count:
            proxy_list.extend(proxy_list)
        proxy_list = proxy_list[:target_count]
    else:
        proxy_list = [None] * target_count

    # 并发请求验证码
    tasks = [captcha_service.get_captcha_info(proxy) for proxy in proxy_list]
    results = await asyncio.gather(*tasks)

    # 合并结果
    captcha_dict = {}
    for result in results:
        if result:
            captcha_dict.update(result)

    return captcha_dict


if __name__ == "__main__":
    # 读取captcha_info.json
    existing_data = {}
    try:
        with open('captcha_info.json', 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        print("未找到现有文件，将创建新文件")

    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    new_result = asyncio.run(main(target_count=10, use_proxy=False))
    print(f"本次获取数据数量: {len(new_result)}")

    # 合并数据
    existing_data.update(new_result)
    print(f"合并后总数据数量: {len(existing_data)}")

    with open('captcha_info.json', 'w') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
