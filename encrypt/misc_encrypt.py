import random


class MiscEncrypt:
    @staticmethod
    def x_b3_traceid() -> str:
        """
        :return: 生成的Trace ID字符串
        """
        characters = "abcdef0123456789"
        trace_id = ''.join(random.choice(characters) for _ in range(16))
        return trace_id
