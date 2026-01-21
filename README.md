# AI内容自动发布系统

> 🚀 全自动 AI 写作 + 多平台发布解决方案

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Powered%20by-Claude%20Code-blue)](https://claude.ai/claude-code)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## ✨ 功能特性

### 🤖 全流程自动化
- ✅ **智能选题**：自动抓取 AI 热点资讯（GitHub Trending、TechCrunch、OpenAI News等）
- ✅ **AI 写作**：使用 Claude Sonnet 4.5 生成 2000-3000 字高质量文章
- ✅ **多平台发布**：一键发布到微信公众号草稿箱 + 小红书
- ✅ **定时任务**：每天 8:00/12:00/18:00 自动执行（可自定义）

### 📝 内容质量保证
- 智能去重（与近48小时内容对比，避免重复）
- 多维度评分系统（基础质量30分 + 时效性20分 + 类型匹配30分 + 受众相关20分）
- 文章质量自动检查（评分≥70分才发布）
- 支持多种内容类型（新工具介绍、实战教程、行业动态等）

### 🎨 微信公众号优化
- 自动格式化为美化的 HTML（代码高亮、样式优化）
- 自动选择精美封面图（从封面库随机选择）
- 支持自定义作者名称

### 📱 小红书适配
- 自动压缩内容到 ≤1000字
- Emoji 风格优化
- 标题自动截断到 ≤20字

## 📋 目录

- [快速开始](#快速开始)
- [详细安装教程](#详细安装教程)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [常见问题](#常见问题)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🚀 快速开始

### 前置要求

1. **Claude Code 账号**（必需）
   - 访问 https://claude.ai/claude-code 注册账号
   - 或使用现有的 Claude 账号

2. **系统要求**
   - Linux/macOS：支持定时任务
   - Windows：需手动运行或使用任务计划程序

3. **Python 环境**
   - Python 3.10+
   - pip 包管理器

### 三步快速安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/ai-content-publisher.git
cd ai-content-publisher

# 2. 运行安装脚本
bash scripts/install.sh

# 3. 配置你的密钥
cp config/config.example.sh config/config.sh
nano config/config.sh  # 编辑配置文件，填入你的密钥
```

### 首次测试运行

```bash
# 测试文章生成
bash skills/ai-content-publisher/auto_publish.sh
```

## 📖 详细安装教程

详见 [docs/INSTALL.md](docs/INSTALL.md)

## ⚙️ 配置说明

### 1. Claude API 配置

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

**获取方式**：
1. 访问 https://console.anthropic.com/settings/keys
2. 点击 "Create Key"
3. 复制生成的 API Key

### 2. 微信公众号配置

```bash
export WECHAT_APPID="your-appid"
export WECHAT_SECRET="your-secret"
```

**获取方式**：
1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入 "设置与开发" -> "基本配置"
3. 复制 AppID 和 AppSecret

**IP白名单设置**：
1. 在微信公众平台 "基本配置" 页面
2. 找到 "IP白名单"
3. 添加你的服务器公网 IP

### 3. 小红书配置

```bash
export XHS_API_URL="http://localhost:18060"
export XHS_IMAGE_DIR="/path/to/xiaohongshu-mcp/docker/images"
```

详细配置见 [docs/xiaohongshu-setup.md](docs/xiaohongshu-setup.md)

## 📚 使用指南

### Linux/macOS 服务器

#### 1. 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 8:00、12:00、18:00 执行）
0 8,12,18 * * * /path/to/ai-content-publisher/skills/ai-content-publisher/auto_publish.sh >> /var/log/ai-content.log 2>&1
```

#### 2. 查看运行日志

```bash
tail -f /var/log/ai-content.log
```

### Windows 系统

详见 [docs/WINDOWS.md](docs/WINDOWS.md)

### 手动运行

```bash
# 进入项目目录
cd /path/to/ai-content-publisher

# 手动执行发布脚本
bash skills/ai-content-publisher/auto_publish.sh
```

## 🛠️ 项目结构

```
ai-content-publisher/
├── config/                      # 配置文件目录
│   ├── config.example.sh        # 配置文件模板
│   └── config.sh                # 实际配置（需自己创建，已在 .gitignore）
├── skills/                      # Claude Code Skills
│   ├── ai-content-publisher/    # 主发布流程
│   ├── wechat-tech-writer/      # 微信文章生成
│   ├── wechat-article-formatter/# 微信格式化
│   ├── wechat-draft-publisher/  # 微信发布
│   └── xiaohongshu-publisher/   # 小红书发布
├── docs/                        # 文档目录
│   ├── INSTALL.md               # 详细安装教程
│   ├── WINDOWS.md               # Windows 使用指南
│   └── xiaohongshu-setup.md     # 小红书配置教程
├── scripts/                     # 工具脚本
│   └── install.sh               # 一键安装脚本
├── README.md                    # 本文件
└── .gitignore                   # Git 忽略配置
```

## ❓ 常见问题

### Q: 文章生成失败，提示 "API 调用失败"？

**A**: 检查以下几点：
1. `ANTHROPIC_API_KEY` 是否正确配置
2. `ANTHROPIC_BASE_URL` 是否可访问
3. API Key 是否有足够的额度
4. 网络连接是否正常

```bash
# 测试 API 连接
python3 -c "
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model='claude-sonnet-4-5-20250929',
    max_tokens=100,
    messages=[{'role': 'user', 'content': '你好'}]
)
print('✅ API 连接正常')
"
```

### Q: 微信公众号发布失败，提示 "IP 不在白名单"？

**A**: 需要在微信公众平台添加服务器 IP 到白名单：

```bash
# 查看服务器公网 IP
curl ifconfig.me
```

### Q: 如何自定义定时任务时间？

**A**: 编辑 crontab，修改时间表达式：

```bash
# 格式：分 时 日 月 周
# 例如每天 9:00 和 21:00
0 9,21 * * * /path/to/auto_publish.sh
```

### Q: Windows 如何设置定时任务？

**A**: 使用任务计划程序，详见 [docs/WINDOWS.md](docs/WINDOWS.md)

### Q: 如何修改文章质量阈值？

**A**: 编辑 `skills/ai-content-publisher/scripts/selector.py`，搜索评分相关代码进行调整。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Claude Code](https://claude.ai/claude-code) - 强大的 AI 编程助手
- [Anthropic](https://www.anthropic.com) - Claude API 提供方
- 所有贡献者和使用者

## 📮 联系方式

- 作者公众号：阳桃AI干货
- GitHub Issues：https://github.com/your-username/ai-content-publisher/issues

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
