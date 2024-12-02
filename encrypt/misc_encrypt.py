import binascii
import hashlib
import random
import string
import time
from collections.abc import Iterable
from numbers import Integral

from typeguard import typechecked

from config import lookup


class CustomFieldDecrypt:
    @staticmethod
    async def random_str(length: Integral) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(random.choice(alphabet) for _ in range(length))

    @staticmethod
    async def base36encode(number: Integral, alphabet: Iterable[str] = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> str:
        """
        将数字转换为base36编码
        Args:
            number: 需要base36的数字
            alphabet: base36的字符集 默认: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
        Returns:
            base36编码后的内容
        """
        base36 = ''
        alphabet = ''.join(alphabet)
        sign = '-' if number < 0 else ''
        number = abs(number)

        while number:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + (base36 or alphabet[0])

    @staticmethod
    async def b64Encode(e: str) -> str:
        P = len(e)
        W = P % 3
        U = []
        z = 16383
        H = 0
        Z = P - W
        while H < Z:
            U.append(await CustomFieldDecrypt.encodeChunk(e, H, Z if H + z > Z else H + z))
            H += z
        if 1 == W:
            F = e[P - 1]
            U.append(lookup[F >> 2] + lookup[(F << 4) & 63] + "==")
        elif 2 == W:
            F = (e[P - 2] << 8) + e[P - 1]
            U.append(lookup[F >> 10] + lookup[63 & (F >> 4)] + lookup[(F << 2) & 63] + "=")
        return "".join(U)

    async def encodeChunk(e, t, r):
        m = []
        for b in range(t, r, 3):
            n = (16711680 & (e[b] << 16)) + \
                ((e[b + 1] << 8) & 65280) + (e[b + 2] & 255)
            m.append(CustomFieldDecrypt.tripletToBase64(n))
        return ''.join(m)

    @staticmethod
    def tripletToBase64(e):
        return (
                lookup[63 & (e >> 18)] + lookup[63 & (e >> 12)] + lookup[(e >> 6) & 63] + lookup[e & 63]
        )


class CookieFieldEncrypt():
    @classmethod
    async def get_a1_and_web_id(cls) -> tuple:
        """
        生成 a1 和 webid
        Returns:
            tuple(a1, webid)
        """
        d = hex(int(time.time() * 1000))[2:] + await CustomFieldDecrypt.random_str(30) + "5" + "0" + "000"
        g = (d + str(binascii.crc32(str(d).encode('utf-8'))))[:52]
        return g, hashlib.md5(g.encode('utf-8')).hexdigest()


class MiscEncrypt(CookieFieldEncrypt):
    @staticmethod
    async def x_b3_traceid() -> str:
        """
        生成 x_b3_traceid
        Returns:
            Trace ID
        """
        characters = "abcdef0123456789"
        trace_id = ''.join(random.choice(characters) for _ in range(16))
        return trace_id

    @staticmethod
    async def search_id():
        e = int(time.time() * 1000) << 64
        t = int(random.uniform(0, 2147483646))
        return await CustomFieldDecrypt.base36encode((e + t))

    @staticmethod
    async def x_xray_traceid(x_b3: str) -> str:
        return hashlib.md5(x_b3.encode('utf-8')).hexdigest()
