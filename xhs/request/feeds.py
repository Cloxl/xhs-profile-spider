# feeds.py

from enum import Enum
from typing import Dict, List, Optional


class FeedType(Enum):
    """推荐流分类"""
    RECOMMEND = "homefeed_recommend"  # 推荐
    FASION = "homefeed.fashion_v3"  # 穿搭
    FOOD = "homefeed.food_v3"  # 美食
    COSMETICS = "homefeed.cosmetics_v3"  # 彩妆
    MOVIE = "homefeed.movie_and_tv_v3"  # 影视
    CAREER = "homefeed.career_v3"  # 职场
    EMOTION = "homefeed.love_v3"  # 情感
    HOUSE = "homefeed.household_product_v3"  # 家居
    GAME = "homefeed.gaming_v3"  # 游戏
    TRAVEL = "homefeed.travel_v3"  # 旅行
    FITNESS = "homefeed.fitness_v3"  # 健身


class Feeds:
    def __init__(self, client):
        self.client = client

    async def get_feed_categories(self) -> List[Dict]:
        """获取主页推荐分类

        Returns:
            分类列表信息
        """
        uri = "/api/sns/web/v1/homefeed/category"
        res = await self.client.get(uri)
        return res["categories"]

    async def get_feed_content(self,
                               feed_type: FeedType,
                               cursor_score: str = "",
                               num: int = 40) -> Dict:
        """获取推荐内容

        Args:
            feed_type: 推荐分类类型
            cursor_score: 分页游标
            num: 获取数量

        Returns:
            推荐内容列表
        """
        uri = "/api/sns/web/v1/homefeed"
        data = {
            "cursor_score": cursor_score,
            "num": num,
            "refresh_type": 1,
            "note_index": 0,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": feed_type.value,
            "search_key": "",
            "need_num": num,
            "image_scenes": ["FD_PRV_WEBP", "FD_WM_WEBP"]
        }
        return await self.client.post(uri, data)

    async def get_search_suggestions(self, keyword: str) -> List[str]:
        """获取搜索关键词建议

        Args:
            keyword: 搜索关键词

        Returns:
            建议关键词列表
        """
        uri = "/api/sns/web/v1/sug/recommend"
        params = {"keyword": keyword}
        res = await self.client.get(uri, params)
        return [sug["text"] for sug in res["sug_items"]]