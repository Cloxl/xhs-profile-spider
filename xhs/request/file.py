import os
from typing import Tuple, List, Dict, Optional
from enum import Enum
from lxml import etree


class FileType(Enum):
    IMAGE = "image"
    VIDEO = "video"


class Uploader:
    def __init__(self, client):
        self.client = client
        self.chunk_size = 5 * 1024 * 1024  # 5MB per chunk

    async def get_upload_permit(self, file_type: FileType, count: int = 1) -> Tuple[str, str]:
        """获取文件上传许可

        Args:
            file_type: 文件类型(图片/视频)
            count: 文件数量

        Returns:
            (file_id, token)元组
        """
        uri = "/api/media/v1/upload/web/permit"
        params = {
            "biz_name": "spectrum",
            "scene": file_type.value,
            "file_count": count,
            "version": "1",
            "source": "web"
        }

        res = await self.client.get(uri, params)
        temp_permit = res["uploadTempPermits"][0]
        file_id = temp_permit["fileIds"][0]
        token = temp_permit["token"]
        return file_id, token

    async def get_upload_id(self, file_id: str, token: str) -> str:
        """获取分片上传ID

        Args:
            file_id: 文件ID
            token: 上传token

        Returns:
            upload_id: 分片上传ID
        """
        headers = {"X-Cos-Security-Token": token}
        res = await self.client.request(
            "POST",
            f"https://ros-upload.xiaohongshu.com/{file_id}?uploads",
            headers=headers
        )
        return self._parse_xml(res.text)["UploadId"]

    async def upload_file(self,
                          file_id: str,
                          token: str,
                          file_path: str,
                          content_type: str = "image/jpeg") -> Dict:
        """上传完整文件

        Args:
            file_id: 文件ID
            token: 上传token
            file_path: 本地文件路径
            content_type: 文件类型

        Returns:
            上传结果
        """
        if os.path.getsize(file_path) > self.chunk_size and content_type == "video/mp4":
            return await self.upload_file_with_chunks(file_id, token, file_path)

        url = f"https://ros-upload.xiaohongshu.com/{file_id}"
        headers = {
            "X-Cos-Security-Token": token,
            "Content-Type": content_type
        }

        with open(file_path, "rb") as f:
            return await self.client.request("PUT", url, data=f, headers=headers)

    async def upload_chunk(self,
                           file_id: str,
                           token: str,
                           chunk_data: bytes,
                           chunk_number: int,
                           upload_id: str) -> Dict:
        """上传单个分片

        Args:
            file_id: 文件ID
            token: 上传token
            chunk_data: 分片数据
            chunk_number: 分片编号
            upload_id: 分片上传ID

        Returns:
            上传结果
        """
        url = f"https://ros-upload.xiaohongshu.com/{file_id}"
        headers = {"X-Cos-Security-Token": token}
        params = {
            "partNumber": chunk_number,
            "uploadId": upload_id
        }

        res = await self.client.request(
            "PUT",
            url,
            params=params,
            data=chunk_data,
            headers=headers
        )

        return {
            "PartNumber": chunk_number,
            "E