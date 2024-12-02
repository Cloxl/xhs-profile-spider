import json
import random
import urllib.parse

from config import ie, lookup


class XscEncrypt:
    """
    提供字符串加密与Base64编码的功能
    """
    @staticmethod
    async def encrypt_encode_utf8(text) -> list:
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

    @staticmethod
    async def triplet_to_base64(e) -> str:
        """
        将24位整数分成4个6位部分 转换为Base64字符串
        Args:
            e: 需要转换的整数
        Returns:
            Base64字符串
        """
        return (lookup[(e >> 18) & 63] + lookup[(e >> 12) & 63] +
                lookup[(e >> 6) & 63] + lookup[e & 63])

    @staticmethod
    async def encode_chunk(e, t, r) -> str:
        """
        将编码后的整数列表分成3字节一组转换为Base64
        Args:
            e: 整数列表
            t: 开始位置
            r: 结束位置
        Returns:
            编码后的Base64字符串
        """
        chunks = []
        for b in range(t, r, 3):
            if b + 2 < len(e):  # 确保有完整的三个字节
                chunk = await XscEncrypt.triplet_to_base64((e[b] << 16) + (e[b + 1] << 8) + e[b + 2])
                chunks.append(chunk)
        return ''.join(chunks)

    @staticmethod
    async def b64_encode(e) -> str:
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
        result = [await XscEncrypt.encode_chunk(e, i, min(i + 16383, Z)) for i in range(0, Z, 16383)]

        if W == 1:
            F = e[-1]
            result.append(lookup[F >> 2] + lookup[(F << 4) & 63] + "==")
        elif W == 2:
            F = (e[-2] << 8) + e[-1]
            result.append(lookup[F >> 10] + lookup[(F >> 4) & 63] + lookup[(F << 2) & 63] + "=")
        return "".join(result)

    @staticmethod
    async def mrc(e) -> int:
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
    
    @staticmethod
    async def encrypt_xsc(xs: str, xt: str, platform: str, a1: str, x1: str, x4: str, b1: str):
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
        x9 = str(await XscEncrypt.mrc(xt+xs+b1))
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
            "x8": b1,
            "x9": x9,
            # "x10": random.randint(10, 29)
            "x10": 24
        }, separators=(",", ":"), ensure_ascii=False)
        return await XscEncrypt.encrypt_encode_utf8(st)


if __name__ == '__main__':
    import asyncio

    t = asyncio.run(XscEncrypt.encrypt_xsc(
        xs="XYW_eyJzaWduU3ZuIjoiNTYiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6ImMyZmU4Nzc4MmFiY2I2YTYzOTFhOTY0MjAyMGI3ZmFjODQ2YjUyMjZmNDIzMmQ5Mjc5YmI1OTYzNjg5NTBlYzg0MzkyZGU3OTY2Y2JkNWQxMzc3NDgzOWJmZTdhNmRjNzEwNDYzMjgzY2ZlNTc3YTcyYTE5ZDhiZDhkMTY4NTQzMGUxNmEwMDc4ZmNhZWE1MzY1NDY0ZjBkYjhhOThhODQ0MmQ2NTg0ODNlNzA5Y2RhNWZmNTk2ZThkMDQwNDQzMjg1OGEwMWYzMGU5OTE3MDVmYWM2MTM3MDU1MGQ3MTkwYjhkMWJkYjM2NjVmNjJjMzQ4YWI0ZTgwYjE0ZjgxNTRjYjMyZGFiMWJiYTZlNzdjZmJkNjA4MTQ1YmNlODc2NDhkNDllYzM2ZDZlMzU2ZjJlZWY5ODEyYWFlN2EwZmZjZjljOGVkZDkxOWIzODJhYTEwMWE5Y2JjOWMxZDVjNmIyYjY3N2M5YjFiYTVlMDU0ZTQ3YjdiN2RiM2NjZWQyZWJjODY2Y2Y4NmRjYjg5MjFkMzA5OTQxMDI3Y2ZjNGIzIn0=",
        xt="1732352811091",
        platform="xhs-pc-web",
        a1="1922f161f3akc5946vixc5zs8ykvvm48u8tt7ele550000297995",
        x1="3.8.7",
        x4="4.44.1",
        b1="I38rHdgsjopgIvesdVwgIC+oIELmBZ5e3VwXLgFTIxS3bqwErFeexd0ekncAzMFYnqthIhJeSBMDKutRI3KsYorWHPtGrbV0P9WfIi/eWc6eYqtyQApPI37ekmR6QL+5Ii6sdneeSfqYHqwl2qt5B0DBIx+PGDi/sVtkIxdsxuwr4qtiIhuaIE3e3LV0I3VTIC7e0utl2ADmsLveDSKsSPw5IEvsiVtJOqw8BuwfPpdeTFWOIx4TIiu6ZPwrPut5IvlaLbgs3qtxIxes1VwHIkumIkIyejgsY/WTge7eSqte/D7sDcpipedeYrDtIC6eDVw2IENsSqtlnlSuNjVtIx5e1qt3bmAeVn8LIESLIEk8+9DUIvzy4I8OIic7ZPwFIviR4o/sDLds6PwVIC7eSd7sf0k4IEve6WGMtVwUIids3s/sxZNeiVtbcUeeYVwRIvM/z06eSuwvgf7sSqweIxltIxZSouwOgVwpsoTHPW5ef7NekuwcIEosSgoe1LuMIiNeWL0sxdh5IiJsxPw9IhR9JPwJPutWIv3e1Vt1IiNs1qw5IEKsdVtFtuw4sqwFIvhvIxqzGniRKWoexVtUIhW4Ii0edqwpBlb2peJsWU4TIiGb4PtOsqwEIvNexutd+pdeVYdsVDEbIhos3odskqt8pqwQIvNeSPwvIieeT/ubIveeSBveDPtXIx0sVqw64B8qIkWJIvvsxFOekaKsDYeeSqwoIkpgIEpYzPwqIxGSIE7eirqSwnvs0VtZIhpBbut14lNedM0eYPwpmPwZIC+7IiGy/VwttVtaIC5e0pesVPwFJqwBIhW="
    ))
    print(t)
