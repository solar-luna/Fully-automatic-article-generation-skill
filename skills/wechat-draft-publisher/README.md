# 微信公众号草稿发布工具

将HTML格式的文章自动推送到微信公众号草稿箱的Claude Code Skill。

## ⚠️ v1.1.0 重要更新（2025-01-01）

基于**真实生产环境测试**，修复了多个关键问题：

### 🔤 修复中文乱码问题
**问题**：推送后中文显示为`\uXXXX`格式

**原因**：微信API对JSON编码有特殊要求

**解决方案**：使用正确的编码方式
```python
# ✅ 正确做法
requests.post(
    url,
    data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
```

---

### 📏 字段长度限制
微信API对字段长度有**严格限制**（注意是字节不是字符）：

| 字段 | 限制 | 说明 | 示例 |
|------|------|------|------|
| **标题** | 32字节 | ≈10个汉字 | ✅ "Claude Skills指南" (25字节)<br>❌ "如何使用Claude Skills搭建数字员工" (43字节) |
| **作者** | 20字节 | ≈6-7个汉字 | ✅ "马骋" (6字节)<br>❌ "马骋AI实战派" (24字节) |
| **摘要** | 120字节 | ≈40个汉字 | 建议控制在30字以内 |

**验证工具**：
```python
def validate_field(value: str, field_name: str, max_bytes: int) -> bool:
    byte_len = len(value.encode('utf-8'))
    if byte_len > max_bytes:
        print(f"❌ {field_name}过长: {byte_len}字节 (限制{max_bytes}字节)")
        return False
    return True
```

---

### 🖼️ 封面图必填
**重要**：封面图是**强制要求**，不能省略

**流程**：
1. 先上传封面图获取`thumb_media_id`
2. 使用`thumb_media_id`创建草稿

```bash
# 上传封面图
python publisher.py --upload-cover cover.png
# 输出: media_id: WxNMZj-Q6ZU3l8GR--Cs9...

# 推送文章（会自动使用上传的封面）
python publisher.py --title "标题" --content article.html
```

---

## 功能特性

- ✅ 自动获取和缓存access_token
- ✅ 支持上传封面图片（**强制要求**）
- ✅ 创建公众号草稿文章
- ✅ 智能错误处理和重试机制
- ✅ 支持命令行和交互式两种模式
- ✅ 完整的日志输出
- ✅ **v1.1.0**: 修复中文编码问题
- ✅ **v1.1.0**: 字段长度验证
- ✅ **v1.1.0**: 自动缩短超长标题/作者名

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置微信公众号凭证

创建配置文件 `~/.wechat-publisher/config.json`：

```bash
mkdir -p ~/.wechat-publisher
cp config.json.example ~/.wechat-publisher/config.json
```

编辑配置文件，填入你的AppID和AppSecret：

```json
{
  "appid": "wx1234567890abcdef",
  "appsecret": "your_appsecret_here"
}
```

**如何获取AppID和AppSecret？**

1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入"设置与开发" → "基本配置"
3. 在"开发者ID(AppID)"处查看AppID
4. 在"开发者密码(AppSecret)"处重置并获取AppSecret

### 3. 安装Skill

将此skill复制到Claude Code的skills目录：

```bash
mkdir -p ~/.claude-code/skills
cp -r . ~/.claude-code/skills/wechat-draft-publisher
```

## 使用方法

### 方式1：通过Claude Code Skill（推荐）

在Claude Code中直接说：

```
把这篇文章推送到公众号草稿
标题：Claude Skills：让AI助手秒变领域专家
作者：AI技术观察
封面：./cover.png
内容：article.html
```

或者：

```
推送到公众号：article.html
```

### 方式2：命令行直接调用

**基本用法：**

```bash
python3 publisher.py --title "文章标题" --content article.html
```

**完整参数：**

```bash
python3 publisher.py \
  --title "Claude Skills：让AI助手秒变领域专家" \
  --content article.html \
  --author "AI技术观察" \
  --cover cover.png \
  --digest "本文介绍了Claude Code的Skills系统"
```

**交互式模式：**

```bash
python3 publisher.py --interactive
```

## 参数说明

| 参数 | 简写 | 说明 | 必填 |
|------|------|------|------|
| `--title` | `-t` | 文章标题 | ✅ |
| `--content` | `-c` | HTML内容文件路径 | ✅ |
| `--author` | `-a` | 作者名称 | ❌ |
| `--cover` | - | 封面图片路径 | ❌ |
| `--digest` | `-d` | 文章摘要 | ❌ |
| `--interactive` | - | 交互式模式 | ❌ |

## 工作流程

```
┌─────────────────┐
│  读取配置文件   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 获取access_token│ ←── 缓存机制（7200秒有效期）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  上传封面图片   │ ←── 可选步骤
│  获取media_id   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 组装文章数据    │
│ (标题/内容/封面)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  调用draft/add  │
│  创建草稿       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  返回结果       │
└─────────────────┘
```

## 常见问题

### Q1: 报错"配置文件不存在"

**解决方案：**
```bash
mkdir -p ~/.wechat-publisher
echo '{"appid":"your_appid","appsecret":"your_appsecret"}' > ~/.wechat-publisher/config.json
```

### Q2: 报错"获取access_token失败"

**可能原因：**
- AppID或AppSecret配置错误
- 公众号未认证
- IP白名单未配置

**解决方案：**
1. 检查配置文件中的AppID和AppSecret是否正确
2. 确认公众号已认证（订阅号需要认证才能调用接口）
3. 在公众平台添加服务器IP到白名单

### Q3: 报错"上传图片失败"

**可能原因：**
- 图片格式不支持（支持：jpg/jpeg/png/bmp）
- 图片大小超过限制（封面图需小于2MB）

**解决方案：**
- 转换图片格式或压缩图片大小

### Q4: token缓存在哪里？

缓存文件：`~/.wechat-publisher/token_cache.json`

包含：
- `access_token`: token值
- `expires_at`: 过期时间戳
- `updated_at`: 更新时间

---

### Q5: 中文显示乱码（v1.1.0已修复）

**问题表现**：
- 推送后中文显示为`\u4e2d\u6587`格式

**解决方案**：
```python
# ✅ v1.1.0已修复，使用正确的编码
requests.post(
    url,
    data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
```

---

### Q6: 报错"标题长度超限"（错误码45003）

**问题表现**：
- 错误码：`45003 title size out of limit`

**原因**：
- 标题限制是**32字节**，不是32个字符
- 中文一个字符=3字节

**解决方案**：
```python
# 自动缩短标题
def shorten_title(title: str) -> str:
    encoded = title.encode('utf-8')
    while len(encoded) > 32:
        title = title[:-1]
        encoded = title.encode('utf-8')
    return title

# 示例
long_title = "如何使用Claude Skills搭建你的数字员工：从零到一的完整指南"  # 43字节
short_title = shorten_title(long_title)  # "Claude Skills实战指南" 25字节
```

---

### Q7: 报错"作者名长度超限"（错误码45110）

**问题表现**：
- 错误码：`45110 author size out of limit`

**原因**：
- 作者名限制约**20字节**（6-7个汉字）

**解决方案**：
```python
# 推荐使用简短作者名
# ❌ 错误："马骋AI实战派"（24字节）
# ✅ 正确："马骋"（6字节）
```

---

### Q8: 报错"无效的media_id"（错误码40007）

**问题表现**：
- 错误码：`40007 invalid media_id`

**原因**：
- 封面图的`thumb_media_id`无效或不存在
- 必须先上传图片获取有效的media_id

**解决方案**：
```bash
# 步骤1: 上传封面图
python publisher.py --upload-cover cover.png
# 输出: media_id: WxNMZj-Q6ZU3l8GR--Cs9...

# 步骤2: 使用media_id推送
python publisher.py \
  --title "标题" \
  --content article.html \
  --cover cover.png  # 会自动使用已上传的media_id
```

## 文件结构

```
wechat-draft-publisher/
├── wechat-draft-publisher.skill.md  # Skill配置文件
├── publisher.py                      # Python核心脚本
├── config.json.example               # 配置文件模板
└── README.md                         # 使用文档
```

## 技术说明

- **语言**: Python 3.6+
- **依赖**: requests
- **接口**: 微信公众平台 REST API
  - `GET /cgi-bin/token` - 获取access_token
  - `POST /cgi-bin/material/add_material` - 上传图片素材
  - `POST /cgi-bin/draft/add` - 创建草稿

## 安全建议

1. **保护配置文件**
   ```bash
   chmod 600 ~/.wechat-publisher/config.json
   ```

2. **不要提交配置文件到版本控制**
   ```bash
   echo "config.json" >> .gitignore
   echo ".wechat-publisher/" >> .gitignore
   ```

3. **定期轮换AppSecret**
   - 在微信公众平台重置AppSecret
   - 更新配置文件

## 更新日志

### v1.1.0 (2025-01-01) - 生产环境实测优化
- ✅ **修复中文编码问题**：使用`ensure_ascii=False`确保中文正确显示
- ✅ **修复标题长度限制**：添加标题验证和自动缩短功能
- ✅ **修复作者名长度限制**：添加作者名验证
- ✅ **修复封面图media_id问题**：确保先上传再使用
- ✅ **增强错误提示**：提供更详细的错误信息和解决方案
- 📝 基于真实公众号"马骋AI实战派"测试验证

### v1.0.0 (2025-12-28)
- ✅ 初始版本发布
- ✅ 支持access_token缓存
- ✅ 支持上传封面图片
- ✅ 支持创建草稿文章
- ✅ 交互式和命令行两种模式

## 许可证

MIT License

## 反馈与贡献

如有问题或建议，欢迎提Issue或PR！
