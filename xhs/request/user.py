from typing import Dict, List, Optional
from datetime import datetime
import json
import asyncio
from enum import Enum


class UserApi:
    def __init__(self, arf):
        """初始化用户API类
        Args:
            arf: AsyncRequestFramework实例
        """
        self.arf = arf
        self._host = "http://edith.xiaohongshu.com"

    async def get_self_info(self) -> Dict:
        """获取当前登录用户信息
        Returns:
            Dict: 用户信息
        """
        uri = "/api/sns/web/v1/user/selfinfo"
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET"
        )
        return response

    async def get_self_info_v2(self) -> Dict:
        """获取当前登录用户信息(v2版本)
        Returns:
            Dict: 用户详细信息
        """
        uri = "/api/sns/web/v2/user/me"
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET"
        )
        return response

    async def get_user_info(self, user_id: str) -> Dict:
        """获取指定用户信息
        Args:
            user_id: 用户ID
        Returns:
            Dict: 用户信息
        """
        uri = "/api/sns/web/v1/user/otherinfo"
        params = {"target_user_id": user_id}
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def follow_user(self, user_id: str) -> Dict:
        """关注用户
        Args:
            user_id: 要关注的用户ID
        Returns:
            Dict: 关注结果
        """
        uri = "/api/sns/web/v1/user/follow"
        data = {"target_user_id": user_id}
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data
        )
        return response

    async def unfollow_user(self, user_id: str) -> Dict:
        """取消关注用户
        Args:
            user_id: 要取消关注的用户ID
        Returns:
            Dict: 取消关注结果
        """
        uri = "/api/sns/web/v1/user/unfollow"
        data = {"target_user_id": user_id}
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data
        )
        return response

    async def get_user_notes(self, user_id: str, cursor: str = "") -> Dict:
        """获取用户发布的笔记列表
        Args:
            user_id: 用户ID
            cursor: 分页游标,默认空字符串
        Returns:
            Dict: {
                "cursor": str,
                "has_more": bool,
                "notes": List[Dict]
            }
        """
        uri = "/api/sns/web/v1/user_posted"
        params = {
            "num": 30,
            "cursor": cursor,
            "user_id": user_id,
            "image_scenes": "FD_WM_WEBP"
        }
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def get_user_collect_notes(self, user_id: str, cursor: str = "", num: int = 30) -> Dict:
        """获取用户收藏的笔记
        Args:
            user_id: 用户ID
            cursor: 分页游标
            num: 每页数量,默认30
        Returns:
            Dict: 收藏笔记列表
        """
        uri = "/api/sns/web/v2/note/collect/page"
        params = {
            "user_id": user_id,
            "num": num,
            "cursor": cursor
        }
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def get_user_liked_notes(self, user_id: str, cursor: str = "", num: int = 30) -> Dict:
        """获取用户点赞的笔记
        Args:
            user_id: 用户ID
            cursor: 分页游标
            num: 每页数量,默认30
        Returns:
            Dict: 点赞笔记列表
        """
        uri = "/api/sns/web/v1/note/like/page"
        params = {
            "user_id": user_id,
            "num": num,
            "cursor": cursor
        }
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def search_users(self,
                           keyword: str,
                           page: int = 1,
                           page_size: int = 20) -> Dict:
        """搜索用户
        Args:
            keyword: 搜索关键词
            page: 页码,默认1
            page_size: 每页数量,默认20
        Returns:
            Dict: 搜索结果列表
        """
        uri = "/api/sns/web/v1/search/usersearch"
        data = {
            "search_user_request": {
                "keyword": keyword,
                "search_id": self._generate_search_id(),
                "page": page,
                "page_size": page_size,
                "biz_type": "web_search_user",
                "request_id": self._generate_request_id()
            }
        }
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data
        )
        return response

    async def get_suggest_users(self, keyword: str = "") -> List[Dict]:
        """获取用户建议(用于@用户)
        Args:
            keyword: 关键词
        Returns:
            List[Dict]: 用户建议列表
        """
        uri = "/web_api/sns/v1/search/user_info"
        data = {
            "keyword": keyword,
            "search_id": self._generate_search_id(),
            "page": {
                "page_size": 20,
                "page": 1
            }
        }
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data
        )
        return response.get("user_info_dtos", [])

    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"search_id_{timestamp}"

    def _generate_request_id(self) -> str:
        """生成请求ID"""
        now = int(datetime.now().timestamp())
        now_ms = int(now * 1000)
        return f"{now}-{now_ms}"
