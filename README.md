<div align="center">
<h1 align="center">小红秀 📄</h1>
<br>
完全开源免费的小红书 <b>数据展示中控!</b>
<br>
</div>

## 功能支持 ✨

- [x] 通过 **HTTP请求** 抓取目标内容
- [x] 自定义规则下载 **爆文**
- [x] 纯算生成 **xs xsc**
- [x] 纯算匹配 **验证码**
- [x] 纯算生成 **轨迹**

### 正在进行中 🚀
-  项目无法绕过法律风险 正在和律师联系 不会用的可以邮箱问我 我有空都会回复
- [ ] 代码结构优化，支持并发与API调用

### 未来计划 📅

- [ ] 批量生成爆文
- [ ] 增加简洁的Web中控界面
- [ ] 增加小号池，实现批量抓取和发布
- [ ] 自定义评论区演戏规则

<details>
    <summary  style="font-size: 20px; font-weight: bold;">如果你只需要纯算xs</summary>

1. 下载 [xs_encrypt.py](https://github.com/Cloxl/xhs-profile-spider/blob/master/encrypt/xs_encrypt.py)
2. 导入 `XsEncrypt` 类，并调用计算 `xs`  

```python  
from xs_encrypt import XsEncrypt 

XsEncrypt.encrypt_xs(url: str, a1: str, ts: str)
```  

- `url`: url去掉host后的字符串，例如：`/api/sns/web/v1/user_posted?num=?&cursor=?&user_id=?&image_formats=?`
- `a1`: Cookies中的a1
- `ts`: 毫秒时间戳(13位数字)  
具体请查看 [#4](https://github.com/Cloxl/xhs-profile-spider/issues/4) 自行扩展

注意:   
请求旋转时验证码时, 加密算法与纯算xs调用方法不同, 应使用`encrypt_sign`方法  
url传入: xt + 'test' + '/api/redcaptcha/v2/captcha/register' + payload  
```python  
xt = str(int(time.time() * 1000))
payload = "{\"secretId\":\"000\",\"verifyType\":\"102\",\"verifyUuid\":\"\",\"verifyBiz\":\"461\",\"sourceSite\":\"\",\"captchaVersion\":\"1.3.0\"}"
url = xt + 'test' + '/api/redcaptcha/v2/captcha/register' + payload

XsEncrypt.encrypt_sign(url: str = url)
```
在纯算纯协议过验证码时 需传递platform参数  
```python
XsEncrypt.encrypt_xs(url: str, a1: str, ts: str, platform: str = 'login')
```
</details>

## ⚠️本项目目前不可直接跑通 在开发中⚠️
    相关代码可以参考使用

## 安装步骤 🛠️

请确保使用 `python >= 3.11`。

```bash
git clone https://github.com/Cloxl/xhshow.git
pip install -r requirements.txt
```
## 运行指令 🚀

配置完成后，运行以下命令：

- 爬取用户发帖数据：
```bash
python xhs.py
```

## 注意事项 ⚠️

- 确保 Cookies 和用户ID正确
- 请遵守法律法规和平台政策

## 常见问题（FAQ） 💬
### 1. 可以爬取个人主页以外的数据吗？ 🔍

具体请查看 [#4](https://github.com/Cloxl/xhshow/issues/4) 自行扩展  

### 2. 如何更新验证码图片?  

code文件夹下有更新验证码的示例  
详细信息查看 [#15](https://github.com/Cloxl/xhshow/issues/15#issuecomment-2484476985)

---
## 开源协议 📝
开源协议为 [MIT](https://github.com/Cloxl/xhshow/blob/master/LICENSE)  
如果你遵循了以下条件:
- 保留 Copyright (c) 2024 Cloxl

那么你可以使用本项目进行以下操作：
- 复制
- 修改
- 分发
- 商用
## 赞助
如果觉得项目对你有帮助, 可以赞助一下  
非常感谢你的支持 我会继续努力完善项目  
<img src="https://github.com/Cloxl/xhshow/blob/master/docs/sponsor.jpg" width="300" height="300" alt="赞助">  
[如果图片加载不出来请点我](https://vip.123pan.cn/1840147130/cdn/%E8%B5%9E%E8%B5%8FCloxl.jpg)

如果你有任何问题 请联系我[邮箱](mailto:cloxl@mail.cloxl.com)
