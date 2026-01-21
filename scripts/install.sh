#!/bin/bash
# AI 内容自动发布系统 - 一键安装脚本

set -e

echo "========================================"
echo "  AI 内容自动发布系统 - 安装向导"
echo "========================================"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    echo "请参考 docs/WINDOWS.md 进行手动安装"
    exit 1
fi

echo "检测到操作系统: $OS"
echo ""

# 检查 Python
echo "1️⃣ 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✅ Python $PYTHON_VERSION 已安装"
else
    echo "❌ 未找到 Python 3"
    echo "请先安装 Python 3.10 或更高版本"
    echo ""
    if [[ "$OS" == "macOS" ]]; then
        echo "macOS 安装命令: brew install python3"
    else
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    fi
    exit 1
fi

# 检查 pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 已安装"
else
    echo "❌ 未找到 pip3"
    exit 1
fi

# 安装 Python 依赖
echo ""
echo "2️⃣ 安装 Python 依赖包..."
pip3 install --user anthropic requests pyyaml feedparser beautifulsoup4 lxml

if [ $? -eq 0 ]; then
    echo "✅ Python 依赖安装完成"
else
    echo "❌ Python 依赖安装失败"
    exit 1
fi

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo ""
echo "3️⃣ 项目目录: $PROJECT_ROOT"

# 检查 Claude Code skills 目录
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
    echo "📁 创建 Claude Code skills 目录..."
    mkdir -p "$CLAUDE_SKILLS_DIR"
fi

# 链接 skills
echo ""
echo "4️⃣ 安装 Claude Code Skills..."
for skill_dir in "$PROJECT_ROOT/skills"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        target="$CLAUDE_SKILLS_DIR/$skill_name"

        if [ -L "$target" ] || [ -d "$target" ]; then
            echo "⚠️  $skill_name 已存在，跳过"
        else
            ln -s "$skill_dir" "$target"
            echo "✅ 已安装: $skill_name"
        fi
    fi
done

# 创建配置文件
echo ""
echo "5️⃣ 配置文件设置..."
CONFIG_FILE="$PROJECT_ROOT/config/config.sh"
CONFIG_EXAMPLE="$PROJECT_ROOT/config/config.example.sh"

if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  配置文件已存在: $CONFIG_FILE"
    read -p "是否覆盖? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "保留现有配置"
    else
        cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
        echo "✅ 配置文件已创建"
    fi
else
    cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
    echo "✅ 配置文件已创建: $CONFIG_FILE"
fi

# 创建日志目录
echo ""
echo "6️⃣ 创建输出目录..."
mkdir -p "$HOME/生成记录"
echo "✅ 输出目录: $HOME/生成记录"

# 创建日志文件
if [ ! -f "/var/log/ai-content.log" ]; then
    if [ -w "/var/log" ]; then
        touch "/var/log/ai-content.log"
        echo "✅ 日志文件: /var/log/ai-content.log"
    else
        touch "$HOME/ai-content.log"
        echo "✅ 日志文件: $HOME/ai-content.log"
        echo "⚠️  无权限写入 /var/log，使用 $HOME/ai-content.log"
    fi
fi

# 完成提示
echo ""
echo "========================================"
echo "  ✅ 安装完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo ""
echo "1️⃣ 编辑配置文件，填入你的密钥："
echo "   nano $CONFIG_FILE"
echo ""
echo "2️⃣ 必需配置项："
echo "   - ANTHROPIC_API_KEY (Claude API 密钥)"
echo "   - WECHAT_APPID 和 WECHAT_SECRET (微信公众号)"
echo ""
echo "3️⃣ 测试运行："
echo "   source $CONFIG_FILE"
echo "   bash ~/.claude/skills/ai-content-publisher/auto_publish.sh"
echo ""
echo "4️⃣ 设置定时任务（可选）："
echo "   crontab -e"
echo "   添加：0 8,12,18 * * * cd $PROJECT_ROOT && source config/config.sh && bash ~/.claude/skills/ai-content-publisher/auto_publish.sh >> /var/log/ai-content.log 2>&1"
echo ""
echo "📚 详细文档："
echo "   - 安装教程: docs/INSTALL.md"
echo "   - 使用指南: README.md"
echo ""
echo "🎉 开始你的 AI 自动化之旅吧！"
echo ""
