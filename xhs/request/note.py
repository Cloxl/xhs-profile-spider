import json
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from config import replacements
from extractor import extract_initial_state
from xhs.request.AsyncRequestFramework import AsyncRequestFramework


class NoteType(Enum):
    NORMAL = "normal"
    VIDEO = "video"


class Notes:
    def __init__(self, arf: AsyncRequestFramework):
        self.arf = arf
        self._host = "https://edith.xiaohongshu.com"

    async def get_note_detail(self, note_id: str, xsec_token: str = "") -> Dict:
        """获取笔记详情

        Args:
            note_id: 笔记ID
            xsec_token: 可选token

        Returns:
            笔记详情信息
        """
        params = {
            "xsec_source": "pc_feed",
            "xsec_token": xsec_token
        }
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
        res = await self.arf.send_http_request(
            url=url,
            method="GET",
            params=params,
            html_mode=True,
            back_fun=True
        )

        content = (await extract_initial_state(await res.acontent(), replacements)
                   )["note"]["noteDetailMap"][f"{note_id}"]

        return content

    async def create_note(self,
                          title: str,
                          desc: str,
                          note_type: NoteType,
                          ats: Optional[List] = None,
                          topics: Optional[List] = None,
                          image_info: Optional[Dict] = None,
                          video_info: Optional[Dict] = None,
                          post_time: Optional[str] = None,
                          is_private: bool = False) -> Dict:
        """创建笔记

        Args:
            title: 标题
            desc: 描述
            note_type: 笔记类型
            ats: @用户列表
            topics: 话题列表
            image_info: 图片信息
            video_info: 视频信息
            post_time: 发布时间
            is_private: 是否私密

        Returns:
            创建结果
        """
        if post_time:
            post_date_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
            post_time = round(int(post_date_time.timestamp()) * 1000)

        uri = "/web_api/sns/v2/note"
        business_binds = {
            "version": 1,
            "noteId": 0,
            "noteOrderBind": {},
            "notePostTiming": {
                "postTime": post_time
            },
            "noteCollectionBind": {
                "id": ""
            }
        }

        data = {
            "common": {
                "type": note_type.value,
                "title": title,
                "note_id": "",
                "desc": desc,
                "source": '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
                "business_binds": json.dumps(business_binds, separators=(",", ":")),
                "ats": ats or [],
                "hash_tag": topics or [],
                "post_loc": {},
                "privacy_info": {"op_type": 1, "type": int(is_private)},
            },
            "image_info": image_info,
            "video_info": video_info,
        }

        headers = {
            "Referer": "https://creator.xiaohongshu.com/"
        }

        return await self.arf.post(uri, data, headers=headers)

    async def like_note(self, note_id: str) -> Dict:
        """点赞笔记"""
        uri = "/api/sns/web/v1/note/like"
        data = {"note_oid": note_id}
        return await self.arf.post(uri, data)

    async def collect_note(self, note_id: str) -> Dict:
        """收藏笔记"""
        uri = "/api/sns/web/v1/note/collect"
        data = {"note_id": note_id}
        return await self.arf.post(uri, data)

    async def get_note_comments(self, note_id: str, cursor: str = "", xsec_token: str = "") -> Dict:
        """获取笔记评论

        Args:
            note_id: 笔记ID
            cursor: 分页游标
            xsec_token: 笔记的xsec_token
        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token
        }

        return await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )

    async def get_sub_comments(self, note_id: str, root_comment_id: str, cursor: str = "", xsec_token: str = "") -> Dict:
        """获取笔记子评论

        Args:
            note_id: 笔记ID
            root_comment_id: 根评论ID
            cursor: 分页游标
            xsec_token: 笔记的xsec_token
        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": "10",
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "top_comment_id": "",
            "xsec_token": xsec_token
        }
        return await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )

    async def search_notes(self,
                           keyword: str,
                           search_id: str,
                           page: int = 1,
                           page_size: int = 20,
                           sort: str = "general",
                           note_type: int = 0) -> Dict:
        """搜索笔记

        Args:
            keyword: 搜索关键词
            search_id: 搜索ID
            page: 页码
            page_size: 每页大小
            sort: 排序方式
            note_type: 笔记类型
        """
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "sort": sort,
            "note_type": note_type,
            "search_id": search_id,
            "image_formats": [
                "jpg",
                "webp",
                "avif"
            ]
        }
        return await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data,
        )

    async def get_note_statistics(self,
                                  page: int = 1,
                                  page_size: int = 48,
                                  sort_by: str = "time",
                                  note_type: int = 0,
                                  time: int = 30,
                                  is_recent: bool = True) -> Dict:
        """获取笔记统计信息

        Args:
            page: 页码
            page_size: 每页大小
            sort_by: 排序方式
            note_type: 笔记类型
            time: 时间范围
            is_recent: 是否最近
        """
        uri = "/api/galaxy/creator/data/note_stats/new"
        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "note_type": note_type,
            "time": time,
            "is_recent": is_recent
        }
        headers = {
            "Referer": "https://creator.xiaohongshu.com/creator/notes?source=official"
        }
        return await self.arf.get(uri, params, headers=headers, is_creator=True)