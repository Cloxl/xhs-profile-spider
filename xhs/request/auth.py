from typing import Dict


class Authentication:
    def __init__(self, arf):
        """初始化认证类
        Args:
            arf: AsyncRequestFramework实例
        """
        self.arf = arf
        self._host = "https://edith.xiaohongshu.com"

    async def get_qrcode(self, qr_type: int = 1) -> Dict:
        """获取登录二维码
        Args:
            qr_type: 二维码类型,默认为1
        Returns:
            Dict: {
                "qr_id": "xxx",
                "code": "xxx",
                "url": "xxx",
                "multi_flag": 0
            }
        """
        uri = "/api/sns/web/v1/login/qrcode/create"
        data = {"qr_type": qr_type}

        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data,
        )
        return response

    async def check_qrcode(self, qr_id: str, code: str) -> Dict:
        """检查二维码扫描状态
        Args:
            qr_id: 二维码ID
            code: 二维码code
        Returns:
            Dict: 二维码状态信息
        """
        uri = "/api/sns/web/v1/login/qrcode/status"
        params = {
            "qr_id": qr_id,
            "code": code
        }

        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def send_sms_code(self, phone: str, zone: str = "86") -> Dict:
        """发送手机验证码
        Args:
            phone: 手机号
            zone: 区号,默认86
        Returns:
            Dict: 发送结果
        """
        uri = "/api/sns/web/v2/login/send_code"
        params = {
            "phone": phone,
            "zone": zone,
            "type": "login"
        }

        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def verify_sms_code(self, phone: str, code: str, zone: str = "86") -> Dict:
        """验证短信验证码
        Args:
            phone: 手机号
            code: 验证码
            zone: 区号,默认86
        Returns:
            Dict: 验证结果
        """
        uri = "/api/sns/web/v1/login/check_code"
        params = {
            "phone": phone,
            "zone": zone,
            "code": code
        }

        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="GET",
            params=params
        )
        return response

    async def login_by_code(self, phone: str, mobile_token: str, zone: str = "86") -> Dict:
        """使用验证码登录
        Args:
            phone: 手机号
            mobile_token: 手机验证token
            zone: 区号,默认86
        Returns:
            Dict: 登录结果
        """
        uri = "/api/sns/web/v1/login/code"
        data = {
            "mobile_token": mobile_token,
            "zone": zone,
            "phone": phone
        }

        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json=data
        )
        return response

    async def activate(self) -> Dict:
        """登录激活
        Returns:
            Dict: 激活结果
        """
        uri = "/api/sns/web/v1/login/activate"
        response = await self.arf.send_http_request(
            url=f"{self._host}{uri}",
            method="POST",
            json={}
        )
        return response

    async def verify_cookie(self, cookie: str) -> bool:
        """验证cookie是否有效
        Args:
            cookie: cookie字符串
        Returns:
            bool: True表示有效,False表示无效
        """
        uri = "/api/sns/web/v1/user/selfinfo"
        try:
            response = await self.arf.send_http_request(
                url=f"{self._host}{uri}",
                method="GET",
                cookie=self._parse_cookie(cookie)
            )
            return True if response else False
        except Exception:
            return False

    def _parse_cookie(self, cookie: str) -> Dict:
        """解析cookie字符串为字典
        Args:
            cookie: cookie字符串
        Returns:
            Dict: cookie字典
        """
        cookie_dict = {}
        if cookie:
            pairs = cookie.split(';')
            for pair in pairs:
                key, value = pair.strip().split('=', 1)
                cookie_dict[key] = value
        return cookie_dict