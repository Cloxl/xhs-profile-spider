<div align="center">
<h1 align="center">小红书推手 📄</h1>
<br>
只需提供目标账户的 <b>UID</b>，全自动复刻爆文！
<br>
</div>

## 功能支持 ✨

- [x] 通过 **HTTP请求** 抓取目标内容
- [x] 自定义规则下载 **爆文**

### 未来计划 📅

- [ ] 代码结构优化，支持并发与API调用
- [ ] 批量生成爆文
- [ ] 增加简洁的Web中控界面
- [ ] 增加小号池，实现批量抓取和发布
- [ ] 自定义评论区演戏规则

<details>
    <summary  style="font-size: 20px; font-weight: bold;">如果你只需要纯算xs</summary>

1. 下载 [EncryptHelper.py](https://raw.githubusercontent.com/Cloxl/xhs-profile-spider/refs/heads/master/EncryptHelper.py)
2. 导入 `EncryptHelper` 类，并调用其方法计算 `xs`  

```python  
from EncryptHelper import EncryptHelper 

EncryptHelper.encrypt_xs(url: str, a1: str, ts: str)
```  

- `url`: url去掉host后的字符串，例如：`/api/sns/web/v1/user_posted?num=?&cursor=?&user_id=?&image_formats=?`
- `a1`: Cookies中的a1
- `ts`: 毫秒时间戳(13位数字)

</details>

## 安装步骤 🛠️

请确保使用 `python >= 3.11`。

```bash
git clone https://github.com/Cloxl/xhs-profile-spider.git
pip install -r requirements.txt
```

## 配置步骤 ⚙️

### 1. 配置 Cookies

在 `xhs.py` 和 `test.py` 中粘贴有效的 Cookies，确保正常访问。

### 2. 配置目标用户ID

在 `xhs.py` 中设置要爬取的用户 ID。

### 3. 搜索示例配置

如需通过关键词搜索，修改 `test.py` 中的 Cookies。

## 运行指令 🚀

配置完成后，运行以下命令：

- 爬取用户发帖数据：
```bash
python xhs.py
```

- 关键词搜索示例：
```bash
python test.py
```

## 注意事项 ⚠️

- 确保 Cookies 和用户ID正确。
- 请遵守法律法规和平台政策。

## 常见问题（FAQ） 💬

### 1. 为什么没有使用并发？ 🕒

目前并发需求不大，后续可能会加入并发优化。

### 2. 为什么代码质量不高？ 🤷‍♂️

目前的代码已足够满足个人需求，未来会考虑优化。

### 3. 可以爬取个人主页以外的数据吗？ 🔍

可以，通过修改参数 `c` 和 `i` 值，实现更多数据的抓取。

---
## 开源协议 📝

开源协议为 [MIT](https://github.com/Cloxl/xhs-profile-spider/blob/master/LICENSE)  
如果你遵循了以下条件：
- 保留 Copyright (c) 2024 Cloxl

那么你可以使用本项目进行以下操作：
- 复制
- 修改
- 分发
- 商用