# 配置文件说明
# 请复制 config.example.sh 为 config.sh，然后填入你的实际配置

# ==================== Claude API 配置 ====================
# 获取方式：https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # 如果使用代理，修改此地址

# ==================== 微信公众号配置 ====================
# 获取方式：登录微信公众平台 -> 设置与开发 -> 基本配置
export WECHAT_APPID="your-wechat-appid-here"
export WECHAT_SECRET="your-wechat-secret-here"

# ==================== 小红书配置 ====================
# 获取方式：参考 docs/xiaohongshu-setup.md
export XHS_API_URL="http://localhost:18060"  # 小红书 API 地址
export XHS_IMAGE_DIR="/path/to/xiaohongshu-mcp/docker/images"  # 小红书图片目录

# ==================== 其他配置 ====================
# 作者名称
export ARTICLE_AUTHOR="你的公众号名称"

# 生成记录保存目录
export OUTPUT_DIR="/home/ubuntu/生成记录"

# 日志文件路径
export LOG_FILE="/var/log/ai-content.log"
