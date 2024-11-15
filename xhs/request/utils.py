# utils.py

from typing import Dict, List, Optional


class Utils:
    def __init__(self, client):
        self.client = client

    async def get_emojis(self) -> List[Dict]:
        """获取表情包列表

        Returns:
            表情包信息列表
        """
        uri = "/api/im/redmoji/detail"
        res = await self.client.get(uri)
        return res["emoji"]["tabs"][0]["collection"]

    async def get_topics(self, keyword: str = "") -> List[Dict]:
        """获取话题信息

        Args:
            keyword: 话题关键词

        Returns:
            话题信息列表
        """
        uri = "/web_api/sns/v1/search/topic"
        data = {
            "keyword": keyword,
            "suggest_topic_request": {
                "title": "",
                "desc": ""
            },
            "page": {
                "page_size": 20,
                "page": 1
            }
        }
        res = await self.client.post(uri, data)
        return res["topic_info_dtos"]

    async def get_ip_info(self) -> Dict:
        """获取IP地址信息

        Returns:
            IP信息,包含地理位置等
        """
        uri = "/api/sns/web/v1/config/ip"
        return await self.client.get(uri)

    async def get_suggest_users(self, keyword: str = "") -> List[Dict]:
        """获取用户建议列表

        Args:
            keyword: 用户名关键词

        Returns:
            用户信息列表
        """
        uri = "/web_api/sns/v1/search/user_info"
        data = {
            "keyword": keyword,
            "search_id": str(time.time() * 1000),
            "page": {
                "page_size": 20,
                "page": 1
            }
        }
        res = await self.client.post(uri, data)
        return res["user_info_dtos"]