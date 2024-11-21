import asyncio
import json
import time
from collections.abc import Mapping
from urllib.parse import urlencode

from curl_cffi.requests import AsyncSession, Response
from loguru import logger

from encrypt import MiscEncrypt, XscEncrypt, XsEncrypt


class AsyncRequestFramework:
    """异步请求框架

    Args:
        verify_ssl (bool, optional): 是否验证 SSL 证书 默认为 True
    """
    def __init__(self, verify_ssl=True):
        self.verify_ssl = verify_ssl

    async def init_session(self):
        """初始化异步会话

        创建一个新的 AsyncSession 实例
        """
        return AsyncSession(
            verify=self.verify_ssl,
            impersonate="chrome124"
        )

    async def close_session(self, session: AsyncSession):
        """关闭异步会话

        如果会话已创建 则关闭会话并将其设置为 None
        """
        return await session.close()

    async def __pre_headers(
        self,
        uri: str,
        xsc_schemas,
        a1: str,
        cookie: dict,
        method: str,
        params: dict,
        data: dict,
    ):
        session = await self.init_session()
        session.cookies.update(cookie)

        xt = str(int(time.time() * 1000))

        match method:
            case 'GET':
                xs = await XsEncrypt.encrypt_xs(url=f"{uri}?{json.dumps(params, separators=(',', ':'), ensure_ascii=False)}",
                                                a1=a1, ts=xt)
            case 'POST':
                xs = await XsEncrypt.encrypt_xs(url=f"{uri}{json.dumps(data,separators=(',', ':'),ensure_ascii=False)}",
                                                a1=a1, ts=xt)
            case _:
                xs = ""

        xsc = await XscEncrypt.encrypt_xsc(xs=xs, xt=xt, platform=xsc_schemas.platform, a1=a1,
                                           x1=xsc_schemas.x1, x4=xsc_schemas.x4)

        session.headers.update({"x-s": xs})
        session.headers.update({"x-t": xt})
        session.headers.update({"x-s-common": xsc})

        x_b3 = await MiscEncrypt.x_b3_traceid()

        session.headers.update({
            "x-b3-traceid": x_b3,
            "x-xray-traceid": await MiscEncrypt.x_xray_traceid(x_b3),
        })

        return session

    async def send_http_request(self, url, method='GET', xsc_schemas=None, uri: str = "", auto_sign: bool = False,
                                params=None, data=None, headers=None, timeout=5, proxy=None, cookie=None, back_fun=False,
                                max_retries=3, retry_delay=0.1, **kwargs):
        """发送 HTTP 请求

        Args:
            url (str): 请求的 URL
            uri (str): 请求的 URI
            xsc_schemas (cls): 可选 xsc的版本信息参数
            auto_sign (bool): 是否自动前面xs 默认为 False
            method (str, optional): HTTP 请求方法 默认为 'GET'
            params (dict, optional): URL 查询参数
            data (dict or str, optional): 发送的请求体数据
            headers (dict, optional): 请求头
            timeout (int, optional): 请求超时时间 默认为 5 秒
            proxy (dict, optional): 代理设置
            cookie (dict, optional): Cookie 信息
            back_fun (bool, optional): 是否返回响应对象 默认为 False
            max_retries (int, optional): 最大重试次数 默认为 3 次
            retry_delay (float, optional): 重试延迟时间 默认为 0.1 秒
            **kwargs: 其他参数

        Returns:
            dict: 返回的 JSON 数据或错误信息
        """

        if headers is None:
            headers = {}
        if proxy == {}:
            proxy = None

        if auto_sign:
            session = await self.__pre_headers(
                uri=uri,
                xsc_schemas=xsc_schemas,
                a1=cookie["a1"],
                cookie=cookie,
                method=method,
                params=params,
                data=data
            )
        else:
            session = AsyncSession()

        method = method.upper()
        kwargs['stream'] = True

        for attempt in range(max_retries):
            try:
                response: Response = await session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    headers=headers,
                    proxy=proxy,
                    timeout=timeout,
                    cookies=cookie,
                    quote=False,
                    **kwargs
                )

                if back_fun:
                    return response

                if response.status_code == 404:
                    logger.error(f" {url} 状态404")
                    return {}

                content = await response.acontent()

                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.exception(e)
                    return content.decode('utf-8', errors='replace')

            except Exception as e:
                logger.error(
                    f"尝试 {attempt + 1}/{max_retries}: {url} data:{json.dumps(data) if isinstance(data, (dict, list)) else data}"
                    f" params:{json.dumps(params) if isinstance(params, (dict, list)) else params} headers: {headers} 请求错误 {e}")
                logger.exception(e)

                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"重试{max_retries}次后仍然失败")
                    return {}

    async def get_redirect_url(self, url: str) -> Mapping:
        """获取重定向 URL

        Args:
            url (str): 原始 URL

        Returns:
            dict: 包含原始 URL、最终 URL 和状态码的字典
        """
        try:
            await self.init_session()
            response = await self.session.get(url, allow_redirects=False)

            if response.status in (301, 302, 303, 307, 308):
                redirect_url = response.headers.get('Location')
                return {
                    'original_url': url,
                    'final_url': redirect_url,
                    'status': response.status
                }

            return {
                'original_url': url,
                'final_url': str(response.url),
                'status': response.status
            }

        except Exception as e:
            return {
                'original_url': url,
                'error': str(e)
            }
