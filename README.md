<div align="center">
<h1 align="center">小红书秀 📄</h1>
<br>
完全开源免费的小红书 <b>数据展示中控!</b>
<br>
</div>

## 功能支持 ✨

- [x] 通过 **HTTP请求** 抓取目标内容
- [x] 自定义规则下载 **爆文**

### 正在进行中 🚀
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
</details>

## ⚠️本项目目前不可直接跑通 在开发中⚠️
    相关代码可以参考使用

## 安装步骤 🛠️

请确保使用 `python >= 3.11`。

```bash
git clone https://github.com/Cloxl/xhs-profile-spider.git
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

具体请查看 [#4](https://github.com/Cloxl/xhs-profile-spider/issues/4) 自行扩展  

---
## 赞助

<div align="center">
    <a href="https://afdian.com/a/Cloxl/plan" target="_blank" style="text-decoration: none;">
        <div style="width: 200px; height: 200px; border-radius: 50%; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 16px; color: #333;">
            反正也没人赞助<br>画个圆吧<br><br>如果真的要赞助<br>点击这个圆即可跳转
        </div>
    </a>
</div>


## 开源协议 📝
开源协议为 [MIT](https://github.com/Cloxl/xhs-profile-spider/blob/master/LICENSE)  
如果你遵循了以下条件:
- 保留 Copyright (c) 2024 Cloxl

那么你可以使用本项目进行以下操作：
- 复制
- 修改
- 分发
- 商用