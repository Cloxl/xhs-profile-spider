import aiohttp
import asyncio
from loguru import logger

from config import headers


async def get_session(cookies: dict) -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    session.headers.update(headers)
    session.cookies = cookies

    return session


async def fetch(url: str, session: aiohttp.ClientSession):
    """
    异步获取URL的内容 处理请求的重试机制
    """
    while True:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    if response.status == 461:
                        logger.warning("验证码问题，请滑动验证！")
                        user_input = input("请输入选项 (输入0跳过当前请求): ")
                        if user_input.strip() == '0':
                            return None  # 跳过当前请求
                    else:
                        logger.error(f"请求失败，状态码: {response.status}")
                        return None
                else:
                    return await response.text()  # 返回响应内容

        except aiohttp.ClientError as e:
            logger.error(f"HTTP请求错误: {str(e)}")
            await asyncio.sleep(2)  # 请求失败后延时重试
