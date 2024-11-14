import asyncio
from typing import Dict, Optional


class Comments:
    def __init__(self, client):
        self.client = client

    async def get_comments(self, note_id: str, cursor: str = "") -> Dict:
        """获取笔记评论列表

        Args:
            note_id: 笔记ID
            cursor: 分页游标

        Returns:
            评论列表数据
        """
        uri = "/api/sns/web/v2/comment/page"
        params = {"note_id": note_id, "cursor": cursor}
        return await self.client.get(uri, params)

    async def get_sub_comments(self,
                               note_id: str,
                               root_comment_id: str,
                               num: int = 30,
                               cursor: str = "") -> Dict:
        """获取评论回复列表

        Args:
            note_id: 笔记ID
            root_comment_id: 父评论ID
            num: 每页数量
            cursor: 分页游标

        Returns:
            子评论列表数据
        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor
        }
        return await self.client.get(uri, params)

    async def create_comment(self,
                             note_id: str,
                             content: str,
                             at_users: Optional[list] = None) -> Dict:
        """发表评论

        Args:
            note_id: 笔记ID
            content: 评论内容
            at_users: @用户列表

        Returns:
            评论创建结果
        """
        uri = "/api/sns/web/v1/comment/post"
        data = {
            "note_id": note_id,
            "content": content,
            "at_users": at_users or []
        }
        return await self.client.post(uri, data)

    async def reply_comment(self,
                            note_id: str,
                            comment_id: str,
                            content: str,
                            at_users: Optional[list] = None) -> Dict:
        """回复评论

        Args:
            note_id: 笔记ID
            comment_id: 要回复的评论ID
            content: 回复内容
            at_users: @用户列表

        Returns:
            评论回复结果
        """
        uri = "/api/sns/web/v1/comment/post"
        data = {
            "note_id": note_id,
            "content": content,
            "target_comment_id": comment_id,
            "at_users": at_users or []
        }
        return await self.client.post(uri, data)

    async def delete_comment(self,
                             note_id: str,
                             comment_id: str) -> Dict:
        """删除评论

        Args:
            note_id: 笔记ID
            comment_id: 要删除的评论ID

        Returns:
            删除结果
        """
        uri = "/api/sns/web/v1/comment/delete"
        data = {
            "note_id": note_id,
            "comment_id": comment_id
        }
        return await self.client.post(uri, data)

    async def like_comment(self,
                           note_id: str,
                           comment_id: str) -> Dict:
        """点赞评论

        Args:
            note_id: 笔记ID
            comment_id: 评论ID

        Returns:
            点赞结果
        """
        uri = "/api/sns/web/v1/comment/like"
        data = {
            "note_id": note_id,
            "comment_id": comment_id
        }
        return await self.client.post(uri, data)

    async def cancel_like_comment(self,
                                  note_id: str,
                                  comment_id: str) -> Dict:
        """取消点赞评论

        Args:
            note_id: 笔记ID
            comment_id: 评论ID

        Returns:
            取消点赞结果
        """
        uri = "/api/sns/web/v1/comment/dislike"
        data = {
            "note_id": note_id,
            "comment_id": comment_id
        }
        return await self.client.post(uri, data)

    async def get_all_comments(self,
                               note_id: str,
                               crawl_interval: int = 1) -> list:
        """获取笔记所有评论(包括子评论)

        Args:
            note_id: 笔记ID
            crawl_interval: 爬取间隔(秒)

        Returns:
            所有评论列表
        """
        result = []
        comments_has_more = True
        comments_cursor = ""

        while comments_has_more:
            comments_res = await self.get_comments(note_id, comments_cursor)
            comments_has_more = comments_res.get("has_more", False)
            comments_cursor = comments_res.get("cursor", "")
            comments = comments_res["comments"]

            for comment in comments:
                result.append(comment)
                cur_sub_comment_count = int(comment["sub_comment_count"])
                cur_sub_comments = comment["sub_comments"]
                result.extend(cur_sub_comments)

                sub_comments_has_more = comment["sub_comment_has_more"] and len(
                    cur_sub_comments) < cur_sub_comment_count
                sub_comment_cursor = comment["sub_comment_cursor"]

                while sub_comments_has_more:
                    page_num = 30
                    sub_comments_res = await self.get_sub_comments(
                        note_id,
                        comment["id"],
                        num=page_num,
                        cursor=sub_comment_cursor
                    )
                    sub_comments = sub_comments_res["comments"]
                    sub_comments_has_more = sub_comments_res["has_more"] and len(sub_comments) == page_num
                    sub_comment_cursor = sub_comments_res["cursor"]
                    result.extend(sub_comments)

                    await asyncio.sleep(crawl_interval)

            await asyncio.sleep(crawl_interval)

        return result