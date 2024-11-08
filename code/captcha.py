import base64
import json
import random

import cv2
import numpy as np
from curl_cffi.requests import AsyncSession
from pyDes import PAD_PKCS5, ECB, des
from code import XhsDesKeys
from config import bg_nums


class CaptchaSolver:
    def __init__(self):
        ...

    async def decrypt_data(self, encoded_data: str) -> str:
        """解密数据
        Args:
            encoded_data: 编码数据
        Return:
            解密后的数据作为字符串
        """
        des_obj = des(XhsDesKeys.DECODE_CAPTCHA_INFO, ECB, padmode=PAD_PKCS5)
        return des_obj.decrypt(base64.b64decode(encoded_data)).decode()

    async def encrypt_data(self, key: str, data: str) -> str:
        """加密数据
        Args:
            data: 待加密数据
        Return:
            加密后的数据
        """
        des_obj = des(key, ECB, padmode=PAD_PKCS5)
        encrypted = des_obj.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    async def decrypt_captcha_info(self, captcha_data: dict) -> tuple[str, dict]:
        """解密验证码信息
        Args:
            captcha_data: 验证码数据
        Return:
            验证码的 rid 和信息字典
        """
        rid = captcha_data['data']['rid']
        captcha_info = json.loads(await self.decrypt_data(captcha_data['data']['captchaInfo']))
        return rid, captcha_info

    async def calculate_mse(self, img1, img2) -> float:
        """计算均方误差
        Args:
            img1: 第一张图像
            img2: 第二张图像
        Return:
            均方误差
        """
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img_resized = cv2.resize(img2_gray, (400, 400))
        img1_binary = cv2.adaptiveThreshold(img1_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
        cropped_square = img_resized[130:270, 130:270]
        img2_binary = cv2.adaptiveThreshold(cropped_square, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
        diff = cv2.absdiff(img1_binary, img2_binary)
        mse = np.mean(np.square(diff))
        return mse

    async def get_distance(self, target_x: int) -> list[list[int]]:
        """生成距离轨迹
        Args:
            target_x: 目标 x 坐标
        Return:
            距离轨迹的列表
        """
        x, y, ts = 1, 0, 0
        result = [[0, y, ts]]
        yflag, y_min, y_max = True, -1, 1

        while x < target_x:
            step_x = random.choice([1, 2])
            repeat_count = random.randint(1, 2)

            for _ in range(repeat_count):
                if x >= target_x:
                    break
                ts += random.randint(1, 7)
                if random.random() < 0.1 and repeat_count == 1:
                    ts += random.randint(20, 70)
                elif x >= (0.95 * target_x):
                    ts += random.randint(20, 70)

                if x >= (0.9 * target_x) and yflag:
                    y += random.randint(y_min, y_max)
                    yflag = False

                result.append([x, y, ts])
            x += step_x

        ts += random.randint(1, 7)
        result.append([target_x, y, ts])
        return result

    async def get_distance_from_info(self, captcha_data: dict) -> None | list[list[int]]:
        """根据验证码数据获取距离
        Args:
            captcha_data: 验证码数据
        Return:
            距离轨迹的列表或 None
        """
        rid, captcha_info = await self.decrypt_captcha_info(captcha_data)
        bg_num = bg_nums.get(captcha_info['backgroundUrl'].split('/')[-1].split('.')[0], None)

        if not bg_num:
            return None

        kwargs = {'stream': True}
        async with AsyncSession() as session:
            response = await session.get(captcha_info['captchaUrl'], **kwargs)
            img2_data = np.frombuffer(await response.acontent(), np.uint8)
            img2 = cv2.imdecode(img2_data, cv2.IMREAD_COLOR)

        img1 = cv2.imread(f'./static/target/center_{bg_num}.png', cv2.IMREAD_COLOR)
        center = (img2.shape[1] // 2, img2.shape[0] // 2)

        angle_dict = {angle: await self.calculate_mse(img1,
                                                      cv2.warpAffine(img2, cv2.getRotationMatrix2D(center, -angle, 1.0),
                                                                     img2.shape[1::-1]))
                      for angle in range(1, 361, 2)}

        return await self.get_distance(int((min(angle_dict, key=angle_dict.get) * 360) / 285))
