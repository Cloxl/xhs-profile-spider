# notifications/notifications.py

from typing import Dict, Optional


class Notifications:
    def __init__(self, client):
        self.client = client

    async def get_mention_notifications(self,
                                        num: int = 20,
                                        cursor: str = "") -> Dict:
        """获取@通知消息

        Args:
            num: 每页数量,默认20条
            cursor: 分页游标

        Returns:
            {
                "has_more": bool,
                "cursor": str,
                "users": list,
                "total_count": int
            }
        """
        uri = "/api/sns/web/v1/you/mentions"
        params = {
            "num": num,
            "cursor": cursor
        }
        return await self.client.get(uri, params)

    async def get_like_notifications(self,
                                     num: int = 20,
                                     cursor: str = "") -> Dict:
        """获取点赞通知消息

        Args:
            num: 每页数量,默认20条
            cursor: 分页游标

        Returns:
            {
                "has_more": bool,
                "cursor": str,
                "users": list,
                "total_count": int,
                "notes": list
            }
        """
        uri = "/api/sns/web/v1/you/likes"
        params = {
            "num": num,
            "cursor": cursor
        }
        return await self.client.get(uri, params)

    async def get_follow_notifications(self,
                                       num: int = 20,
                                       cursor: str = "") -> Dict:
        """获取关注通知消息

        Args:
            num: 每页数量,默认20条
            cursor: 分页游标

        Returns:
            {
                "has_more": bool,
                "cursor": str,
                "users": list,
                "total_count": int
            }
        """
        uri = "/api/sns/web/v1/you/connections"
        params = {
            "num": num,
            "cursor": cursor
        }
        return await self.client.get(uri, params)

    async def get_all_notifications(self,
                                    limit: Optional[int] = None) -> Dict[str, list]:
        """获取所有类型的通知消息

        Args:
            limit: 限制每种通知的获取数量,默认获取全部

        Returns:
            {
                "mentions": list,
                "likes": list,
                "follows": list
            }
        """
        results = {
            "mentions": [],
            "likes": [],
            "follows": []
        }

        # 获取@通知
        cursor = ""
        while True:
            res = await self.get_mention_notifications(cursor=cursor)
            results["mentions"].extend(res.get("users", []))

            if not res.get("has_more") or (limit and len(results["mentions"]) >= limit):
                break
            cursor = res.get("cursor", "")

        # 获取点赞通知
        cursor = ""
        while True:
            res = await self.get_like_notifications(cursor=cursor)
            results["likes"].extend(res.get("users", []))

            if not res.get("has_more") or (limit and len(results["likes"]) >= limit):
                break
            cursor = res.get("cursor", "")

        # 获取关注通知
        cursor = ""
        while True:
            res = await self.get_follow_notifications(cursor=cursor)
            results["follows"].extend(res.get("users", []))

            if not res.get("has_more") or (limit and len(results["follows"]) >= limit):
                break
            cursor = res.get("cursor", "")

        # 如果设置了limit,截取指定数量
        if limit:
            results["mentions"] = results["mentions"][:limit]
            results["likes"] = results["likes"][:limit]
            results["follows"] = results["follows"][:limit]

        return results

    async def mark_notifications_read(self, notification_ids: list) -> Dict:
        """标记通知为已读

        Args:
            notification_ids: 通知ID列表

        Returns:
            API响应结果
        """
        uri = "/api/sns/web/v1/notifications/mark_read"
        data = {
            "notification_ids": notification_ids
        }
        return await self.client.post(uri, data)