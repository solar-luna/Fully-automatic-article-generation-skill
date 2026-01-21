# 快速参考

## 🚀 最快 5 分钟上手

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/ai-content-publisher.git
cd ai-content-publisher

# 2. 安装
bash scripts/install.sh

# 3. 配置
cp config/config.example.sh config/config.sh
nano config/config.sh  # 填入你的 API Key

# 4. 运行
source config/config.sh
bash ~/.claude/skills/ai-content-publisher/auto_publish.sh
```

## 📝 常用命令

### 手动生成文章

```bash
source config/config.sh
python3 ~/.claude/skills/wechat-tech-writer/generate.py \
  --topic "你的文章标题" \
  --url "参考链接" \
  --type "new_tool" \
  --output "$HOME/生成记录/$(date +%Y-%m-%d)" \
  --mode standard
```

### 查看日志

```bash
tail -f /var/log/ai-content.log
```

### 测试 API 连接

```bash
source config/config.sh
python3 << 'EOF'
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=50,
    messages=[{"role": "user", "content": "你好"}]
)
print("✅ API 正常")
EOF
```

## ⚙️ 配置模板

### 最小配置

```bash
# config/config.sh
export ANTHROPIC_API_KEY="your-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

### 完整配置

```bash
# Claude API
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"

# 微信公众号
export WECHAT_APPID="your-appid"
export WECHAT_SECRET="your-secret"

# 小红书
export XHS_API_URL="http://localhost:18060"
export XHS_IMAGE_DIR="/path/to/images"

# 其他
export ARTICLE_AUTHOR="你的公众号名称"
export OUTPUT_DIR="$HOME/生成记录"
export LOG_FILE="/var/log/ai-content.log"
```

## 🔧 定时任务

### crontab 格式

```
# 分 时 日 月 周 命令
# 每天 8:00
0 8 * * * /path/to/command

# 每天 8:00、12:00、18:00
0 8,12,18 * * * /path/to/command

# 每隔2小时
0 */2 * * * /path/to/command
```

### 实际示例

```bash
# 编辑 crontab
crontab -e

# 添加任务（每天 8:00、12:00、18:00）
0 8,12,18 * * * cd ~/ai-content-publisher && source config/config.sh && bash ~/.claude/skills/ai-content-publisher/auto_publish.sh >> /var/log/ai-content.log 2>&1
```

## 🐛 快速排错

### 问题：API 调用失败

```bash
# 检查 API Key
echo $ANTHROPIC_API_KEY

# 测试网络
curl -I https://api.anthropic.com

# 查看详细错误
python3 -c "from anthropic import Anthropic; Anthropic().messages.create(model='claude-sonnet-4-5-20250929', max_tokens=10, messages=[{'role': 'user', 'content': 'hi'}])"
```

### 问题：文章生成为空

```bash
# 检查输出目录
ls -lh ~/生成记录/$(date +%Y-%m-%d)/

# 查看日志
tail -50 /var/log/ai-content.log

# 手动测试
python3 ~/.claude/skills/wechat-tech-writer/generate.py --topic "测试" --url "https://example.com" --type "new_tool" --output "/tmp/test" --mode standard
```

### 问题：定时任务不运行

```bash
# 检查 crontab
crontab -l

# 检查 cron 服务
sudo systemctl status cron  # Ubuntu/Debian
sudo systemctl status crond  # CentOS/RHEL

# 查看 cron 日志
sudo tail -f /var/log/syslog | grep CRON  # Ubuntu/Debian
sudo tail -f /var/log/cron  # CentOS/RHEL
```

## 📊 项目结构速查

```
ai-content-publisher/
├── config/               # 配置文件
│   └── config.sh        # 你的配置（需创建）
├── skills/              # Claude Skills
│   ├── ai-content-publisher/
│   ├── wechat-tech-writer/
│   ├── wechat-article-formatter/
│   ├── wechat-draft-publisher/
│   └── xiaohongshu-publisher/
├── docs/                # 文档
│   ├── INSTALL.md
│   └── WINDOWS.md
└── scripts/             # 工具脚本
    └── install.sh
```

## 🔗 有用的链接

- Claude API: https://console.anthropic.com/settings/keys
- 微信公众平台: https://mp.weixin.qq.com
- 项目 Issues: https://github.com/your-username/ai-content-publisher/issues

## 💡 小技巧

### 1. 批量生成多篇文章

```bash
for topic in "AI技术1" "AI技术2" "AI技术3"; do
    python3 ~/.claude/skills/wechat-tech-writer/generate.py \
        --topic "$topic" \
        --url "https://example.com" \
        --type "new_tool" \
        --output "$HOME/生成记录/$(date +%Y-%m-%d)/$topic" \
        --mode standard
done
```

### 2. 查看生成的所有文章

```bash
find ~/生成记录 -name "article.md" -exec echo "=== {} ===" \; -exec head -5 {} \; -exec echo "" \;
```

### 3. 统计本月生成的文章数

```bash
find ~/生成记录/$(date +%Y-%m)* -name "article.md" 2>/dev/null | wc -l
```

---

📚 完整文档: [README.md](README.md) | [INSTALL.md](docs/INSTALL.md)
