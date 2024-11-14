import json
import random
import urllib.parse
from config import lookup, ie


class XscEncrypt:
    """
    提供字符串加密与Base64编码的功能
    """

    def __init__(self):
        """初始化Encoder实例"""
        self.lookup = lookup

    async def encrypt_encode_utf8(self, text) -> list:
        """
        对输入的文本进行URL编码 转换百分号编码为十进制ASCII值
        Args:
            text: 需要编码的字符串
        Returns:
            编码后的整数列表
        """
        encoded = urllib.parse.quote(text)
        return [int(encoded[i + 1:i + 3], 16) if encoded[i] == '%' else ord(encoded[i])
                for i in range(len(encoded)) if encoded[i] != '%' or i % 3 == 0]

    async def triplet_to_base64(self, e) -> str:
        """
        将24位整数分成4个6位部分 转换为Base64字符串
        Args:
            e: 需要转换的整数
        Returns:
            Base64字符串
        """
        return (self.lookup[(e >> 18) & 63] + self.lookup[(e >> 12) & 63] +
                self.lookup[(e >> 6) & 63] + self.lookup[e & 63])

    async def encode_chunk(self, e, t, r) -> str:
        """
        将编码后的整数列表分成3字节一组转换为Base64
        Args:
            e: 整数列表
            t: 开始位置
            r: 结束位置
        Returns:
            编码后的Base64字符串
        """
        return ''.join(await self.triplet_to_base64((e[b] << 16) + (e[b + 1] << 8) + e[b + 2])
                       for b in range(t, r, 3))

    async def b64_encode(self, e) -> str:
        """
        将整数列表编码为Base64格式
        Args:
            e: 整数列表
        Returns:
            Base64字符串
        """
        P = len(e)
        W = P % 3
        Z = P - W
        result = [await self.encode_chunk(e, i, min(i + 16383, Z)) for i in range(0, Z, 16383)]

        if W == 1:
            F = e[-1]
            result.append(self.lookup[F >> 2] + self.lookup[(F << 4) & 63] + "==")
        elif W == 2:
            F = (e[-2] << 8) + e[-1]
            result.append(self.lookup[F >> 10] + self.lookup[(F >> 4) & 63] + self.lookup[(F << 2) & 63] + "=")
        return "".join(result)

    async def mrc(self, e) -> int:
        """
        使用自定义CRC算法生成校验值
        Args:
            e: 输入字符串
        Returns:
            32位整数校验值
        """
        o = -1

        def unsigned_right_shift(r, n=8):
            return (r + (1 << 32)) >> n & 0xFFFFFFFF if r < 0 else (r >> n) & 0xFFFFFFFF

        def to_js_int(num):
            return (num + 2 ** 31) % 2 ** 32 - 2 ** 31

        for char in e:
            o = to_js_int(ie[(o & 255) ^ ord(char)] ^ unsigned_right_shift(o, 8))
        return to_js_int(~o ^ 3988292384)

    async def encrypt_xsc(self, xs: str, xt: str, platform: str, a1: str, x1: str, x4: str) -> str:
        """
        生成xsc
        Args:
            xs: 输入字符串
            xt: 输入时间戳
            platform: 平台信息
            a1: 浏览器特征
            x1: xsc版本
            x4: 内部版本
            b1: 浏览器指纹
        Returns:
            xsc
        """
        st = json.dumps({
            "s0": 5,
            "s1": "",
            "x0": "1",
            "x1": x1,
            "x2": "Windows",
            "x3": platform,
            "x4": x4,
            "x5": a1,
            "x6": xt,
            "x7": xs,
            "x8": "I38rH",
            "x9": int,
            "x10": random.randint(10, 29)
        }, separators=(",", ":"), ensure_ascii=False)

        encrypted_data = await self.encrypt_encode_utf8(str(await self.mrc(st)))
        return await self.b64_encode(encrypted_data)
