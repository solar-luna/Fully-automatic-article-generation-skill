# 小红书自动发布工具

自动将微信公众号内容转换为小红书格式并发布的工具。

## 功能特点

- ✅ **智能格式转换**: 将微信HTML内容转换为小红书纯文本格式
- ✅ **智能摘要**: 自动将2000-3000字文章压缩到800字以内
- ✅ **自动封面图**: 使用Pillow库自动生成文字封面图
- ✅ **MCP集成**: 通过xiaohongshu-mcp服务直接发布

## 安装

### 1. 安装Python依赖

```bash
pip install Pillow requests
```

### 2. 部署xiaohongshu-mcp服务

```bash
# 创建目录
mkdir -p ~/xiaohongshu-mcp
cd ~/xiaohongshu-mcp

# 下载配置文件
wget https://raw.githubusercontent.com/xpzouying/xiaohongshu-mcp/main/docker/docker-compose.yml

# 首次登录（只需一次）
docker compose up xiaohongshu-login
# 扫码登录后 Ctrl+C 退出

# 启动服务
docker compose up -d
```

服务将运行在 `http://localhost:18060/mcp`

## 使用方法

### 方式1: 从微信HTML发布

```bash
python publisher.py --wechat \
  --title "OpenAI o4模型重磅发布" \
  --content article.html
```

### 方式2: 直接发布

```bash
python publisher.py --direct \
  --title "测试标题" \
  --content "内容文本" \
  --images cover.jpg
```

### 方式3: 使用JSON配置

```bash
python publisher.py --config article.json
```

配置文件格式:
```json
{
  "mode": "wechat",
  "title": "文章标题",
  "content": "article.html"
}
```

## 内容适配规则

| 项目 | 微信公众号 | 小红书 |
|------|-----------|--------|
| 标题 | 不限制 | 最多20字 |
| 正文 | 2000-3000字 | 最多800字（含emoji） |
| 图片 | 多张 | 最多9张 |
| 格式 | HTML | 纯文本+emoji |

## 目录结构

```
~/.claude/skills/xiaohongshu-publisher/
├── SKILL.md              # Skill定义
├── publisher.py          # 主发布脚本
├── README.md             # 本文档
└── scripts/
    ├── content_adapter.py    # 内容适配器
    ├── image_generator.py    # 封面图生成器
    └── xiaohongshu_client.py # MCP客户端
```

## 开发

### 测试内容适配器

```bash
cd ~/.claude/skills/xiaohongshu-publisher/scripts
python content_adapter.py
```

### 测试封面图生成

```bash
cd ~/.claude/skills/xiaohongshu-publisher/scripts
python image_generator.py
```

### 测试MCP连接

```bash
cd ~/.claude/skills/xiaohongshu-publisher/scripts
python xiaohongshu_client.py
```

## 常见问题

### MCP服务连接失败

确保xiaohongshu-mcp服务正在运行:
```bash
cd ~/xiaohongshu-mcp
docker compose ps
docker compose logs -f
```

### 登录状态过期

重新登录:
```bash
cd ~/xiaohongshu-mcp
docker compose up xiaohongshu-login
```

### 字体显示问题

如果封面图字体显示不正常，请安装系统字体:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# macOS
# 系统自带PingFang字体

# Windows
# 系统自带微软雅黑字体
```

## 参考资料

- [xiaohongshu-mcp GitHub](https://github.com/xpzouying/xiaohongshu-mcp)
- [xiaohongshu-mcp Docker Hub](https://hub.docker.com/r/xpzouying/xiaohongshu-mcp)
- [小红书运营规范](https://www.xiaohongshu.com/)

## License

MIT
