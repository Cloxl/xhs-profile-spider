import base64
import json
import random
from code import XhsDesKeys
import cv2
import numpy as np
from curl_cffi.requests import AsyncSession
from pyDes import ECB, PAD_PKCS5, des
from config import bg_nums


class CaptchaSolver:
    def __init__(self):
        pass

    async def decrypt_data(self, encoded_data: str, decode_key: str = XhsDesKeys.DECODE_CAPTCHA_INFO) -> str:
        """解密数据"""
        des_obj = des(decode_key, ECB, padmode=PAD_PKCS5)
        return des_obj.decrypt(base64.b64decode(encoded_data)).decode()

    async def encrypt_data(self, key: str, data: str) -> str:
        """加密数据"""
        des_obj = des(key, ECB, padmode=PAD_PKCS5)
        encrypted = des_obj.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    async def decrypt_captcha_info(self, captcha_data: dict) -> tuple[str, dict]:
        """解密验证码信息"""
        rid = captcha_data['data']['rid']
        captcha_info = json.loads(await self.decrypt_data(captcha_data['data']['captchaInfo']))
        return rid, captcha_info

    async def calculate_mse(self, img1, img2) -> float:
        """计算均方误差"""
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
        """生成距离轨迹"""
        trace = self.generate_trace(target_x)
        return trace

    def generate_trace(self, distance):
        def smooth_trace(trace):
            """
            平滑轨迹，确保合理性
            """
            # 确保时间严格递增
            for i in range(1, len(trace)):
                if trace[i][2] <= trace[i - 1][2]:
                    trace[i][2] = trace[i - 1][2] + random.randint(5, 15)

            # 平滑x坐标
            smoothed = [trace[0]]
            for i in range(1, len(trace) - 1):
                smoothed_x = (trace[i - 1][0] + trace[i][0] + trace[i + 1][0]) / 3
                smoothed.append([int(smoothed_x), trace[i][1], trace[i][2]])
            smoothed.append(trace[-1])

            return smoothed

        trace = []
        trace.append([0, 0, 0])

        current_x = 0
        current_y = 0
        current_time = 0

        need_y_offset = random.random() < 0.7
        if need_y_offset:
            y_offset = random.randint(6, 12)
        else:
            y_offset = 0

        # 加速阶段：前60%距离
        while current_x < distance * 0.6:
            step = random.randint(5, 20)  # 加速步长，增加变化范围
            current_x += step

            if need_y_offset and current_x > distance * 0.2 and current_y == 0:
                current_y = y_offset

            current_time += random.randint(10, 20)  # 随机调整时间间隔
            trace.append([current_x, current_y, current_time])

        # 减速和回退阶段：后40%距离
        deceleration_point = distance * random.uniform(0.6, 0.8)
        while current_x < distance:
            if current_x >= deceleration_point and random.random() < 0.5:  # 50%概率减速
                step = random.randint(1, 4)  # 减速步长较小
            else:
                step = random.randint(2, 6)  # 稍大步长

            current_x += step
            current_time += random.randint(15, 25)  # 调整时间间隔

            # 偶尔停顿
            if random.random() < 0.1:  # 10%概率停顿
                pause_duration = random.randint(100, 300)  # 停顿100到300毫秒
                current_time += pause_duration

            # 可能的轻微回退
            if random.random() < 0.2 and current_x > distance * 0.7:
                retreat_step = random.randint(1, 3)
                current_x -= retreat_step
                current_time += random.randint(20, 40)

            trace.append([min(current_x, distance), current_y, current_time])

            # 可能的过冲和回退
            if current_x >= distance:
                if random.random() < 0.6:  # 60%几率过冲
                    overshoot = random.randint(1, 5)
                    current_x = distance + overshoot
                    current_time += random.randint(20, 40)
                    trace.append([current_x, current_y, current_time])

                    # 快速回退到正确位置
                    retreat_distance = random.randint(1, 3)
                    current_x = distance - retreat_distance
                    current_time += random.randint(50, 80)
                    trace.append([current_x, current_y, current_time])

                break

        # 最终校准
        if trace[-1][0] != distance:
            for _ in range(random.randint(1, 3)):
                current_x += random.randint(-2, 2)
                current_time += random.randint(30, 50)
                current_x = max(distance - 3, min(current_x, distance + 1))

                if random.random() < 0.3:
                    current_y += random.randint(-1, 1)
                    current_y = max(0, min(current_y, 14))

                trace.append([current_x, current_y, current_time])

        # 确保最后一个点是目标距离
        if trace[-1][0] != distance:
            current_time += random.randint(20, 40)
            trace.append([distance, current_y, current_time])

        # 平滑处理
        trace = smooth_trace(trace)

        return trace

    async def get_distance_from_info(self, captcha_data: dict) -> None | list[list[int]]:
        """根据验证码数据获取距离"""
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
