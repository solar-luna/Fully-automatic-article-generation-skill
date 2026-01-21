# 详细安装教程

本文档将引导你一步步完成 AI 内容自动发布系统的完整安装和配置。

## 📋 安装前准备

### 1. 检查系统环境

```bash
# 检查 Python 版本（需要 3.10+）
python3 --version

# 检查 pip
pip3 --version

# 检查 git
git --version
```

如果缺少任何工具，请先安装：

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```

**macOS**:
```bash
brew install python3 git
```

### 2. 获取必要的密钥和凭据

在开始安装前，请准备好以下信息：

- [ ] Claude API Key（必需）
- [ ] 微信公众号 AppID 和 AppSecret（可选）
- [ ] 小红书 API 配置（可选）

## 🚀 完整安装步骤

### 步骤 1：克隆项目

```bash
# 进入你的工作目录
cd ~

# 克隆仓库
git clone https://github.com/your-username/ai-content-publisher.git

# 进入项目目录
cd ai-content-publisher

# 查看项目结构
ls -la
```

### 步骤 2：安装 Python 依赖

```bash
# 安装 anthropic SDK
pip3 install anthropic

# 安装其他依赖
pip3 install requests pyyaml feedparser beautifulsoup4 lxml

# 验证安装
python3 -c "import anthropic; print('✅ anthropic 安装成功')"
```

###步骤 3：配置 Claude Code Skills

```bash
# 创建 skills 目录（如果不存在）
mkdir -p ~/.claude/skills

# 链接或复制 skills 到 Claude Code 目录
cp -r skills/* ~/.claude/skills/

# 或使用软链接（推荐，便于更新）
ln -s $(pwd)/skills/* ~/.claude/skills/

# 验证
ls ~/.claude/skills/
```

你应该看到：
```
ai-content-publisher
wechat-article-formatter
wechat-draft-publisher
wechat-tech-writer
xiaohongshu-publisher
```

### 步骤 4：创建配置文件

```bash
# 复制配置模板
cp config/config.example.sh config/config.sh

# 编辑配置文件
nano config/config.sh  # 或使用 vim、vi 等编辑器
```

### 步骤 5：配置 Claude API

编辑 `config/config.sh`，填入你的 Claude API 密钥：

```bash
export ANTHROPIC_API_KEY="sk-ant-your-actual-api-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

**测试 API 连接**：

```bash
# 加载配置
source config/config.sh

# 测试连接
python3 << 'PYTHON'
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=100,
    messages=[{"role": "user", "content": "你好，请用中文回复"}]
)
print("✅ API 测试成功！")
for block in response.content:
    if hasattr(block, 'text'):
        print("Claude 回复:", block.text)
PYTHON
```

### 步骤 6：配置微信公众号（可选）

#### 6.1 获取 AppID 和 AppSecret

1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入 "设置与开发" → "基本配置"
3. 复制 "开发者ID(AppID)" 和 "开发者密码(AppSecret)"

#### 6.2 设置 IP 白名单

1. 在 "基本配置" 页面找到 "IP白名单"
2. 点击 "修改"
3. 添加你的服务器公网 IP

**获取服务器 IP**：
```bash
curl ifconfig.me
```

#### 6.3 配置文件设置

编辑 `config/config.sh`：

```bash
export WECHAT_APPID="wxYOUR_APPID_HERE"
export WECHAT_SECRET="YOUR_SECRET_HERE"
```

#### 6.4 测试微信 API

```bash
source config/config.sh

python3 << 'PYTHON'
import os
import requests

appid = os.getenv('WECHAT_APPID')
secret = os.getenv('WECHAT_SECRET')

url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
response = requests.get(url)
data = response.json()

if 'access_token' in data:
    print("✅ 微信 API 测试成功！")
    print(f"Access Token: {data['access_token'][:20]}...")
else:
    print("❌ 微信 API 测试失败")
    print(f"错误信息: {data}")
PYTHON
```

### 步骤 7：配置小红书（可选）

详见 [xiaohongshu-setup.md](xiaohongshu-setup.md)

### 步骤 8：测试文章生成

```bash
# 加载配置
source config/config.sh

# 测试生成单篇文章
python3 ~/.claude/skills/wechat-tech-writer/generate.py \
  --topic "测试：AI 写作工具使用指南" \
  --url "https://www.example.com" \
  --type "new_tool" \
  --output "/tmp/test_article" \
  --mode standard

# 检查生成结果
ls -lh /tmp/test_article/
cat /tmp/test_article/article.md | head -20
```

### 步骤 9：测试完整发布流程

```bash
# 运行完整的自动发布脚本
bash ~/.claude/skills/ai-content-publisher/auto_publish.sh

# 观察输出，确保每个步骤都成功
# 检查生成的文章
ls -lh ~/生成记录/$(date +%Y-%m-%d)/
```

### 步骤 10：设置定时任务（Linux/macOS）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 8:00、12:00、18:00 执行）
0 8,12,18 * * * cd ~/ai-content-publisher && source config/config.sh && bash ~/.claude/skills/ai-content-publisher/auto_publish.sh >> /var/log/ai-content.log 2>&1

# 保存并退出（按 ESC，输入 :wq）

# 验证 crontab
crontab -l
```

**创建日志文件**：
```bash
sudo touch /var/log/ai-content.log
sudo chown $USER:$USER /var/log/ai-content.log
```

## ✅ 验证安装

运行以下命令验证所有组件：

```bash
# 1. 验证 Python 环境
python3 -c "import anthropic, requests, yaml; print('✅ Python 依赖正常')"

# 2. 验证 Skills 安装
ls ~/.claude/skills/ai-content-publisher && echo "✅ Skills 安装正常"

# 3. 验证配置文件
test -f ~/ai-content-publisher/config/config.sh && echo "✅ 配置文件存在"

# 4. 验证 API 连接
source ~/ai-content-publisher/config/config.sh && \
python3 -c "from anthropic import Anthropic; Anthropic().messages.create(model='claude-sonnet-4-5-20250929', max_tokens=10, messages=[{'role': 'user', 'content': 'hi'}]); print('✅ Claude API 正常')"

# 5. 验证定时任务
crontab -l | grep ai-content-publisher && echo "✅ 定时任务已设置"
```

## 🐛 常见安装问题

### 问题 1：pip install anthropic 失败

**错误**：`Could not find a version that satisfies the requirement anthropic`

**解决方案**：
```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 重试安装
pip3 install anthropic
```

### 问题 2：权限错误

**错误**：`Permission denied`

**解决方案**：
```bash
# 不要使用 sudo pip，使用用户安装
pip3 install --user anthropic

# 或创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install anthropic
```

### 问题 3：crontab 任务不执行

**排查步骤**：

1. 检查 crontab 语法：
```bash
crontab -l
```

2. 手动执行脚本测试：
```bash
cd ~/ai-content-publisher && source config/config.sh && bash ~/.claude/skills/ai-content-publisher/auto_publish.sh
```

3. 检查日志：
```bash
tail -f /var/log/ai-content.log
```

4. 确保路径正确（使用绝对路径）

### 问题 4：文章生成超时

**可能原因**：
- 网络连接不稳定
- API 配置错误
- 代理设置问题

**解决方案**：
```bash
# 测试网络
curl -I https://api.anthropic.com

# 检查 API Key
echo $ANTHROPIC_API_KEY

# 如果使用代理，配置代理
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

## 📞 获取帮助

如果遇到问题：

1. 查看 [常见问题](../README.md#常见问题)
2. 查看 [GitHub Issues](https://github.com/your-username/ai-content-publisher/issues)
3. 提交新的 Issue 并附上：
   - 错误信息完整截图
   - 系统环境信息 (`python3 --version`, `uname -a`)
   - 执行的命令

## 🎉 安装完成

恭喜！你已经成功安装了 AI 内容自动发布系统。

**下一步**：
- 阅读 [README.md](../README.md) 了解详细使用方法
- 查看 [WINDOWS.md](WINDOWS.md) 了解 Windows 系统使用方法
- 开始你的第一次自动发布！

---

📚 返回 [主文档](../README.md)
