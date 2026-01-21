#!/bin/bash
# AI内容自动发布脚本 - 完整版
# 每天自动获取热点、生成文章、发布到微信公众号草稿箱

set -e
set -o pipefail  # 确保管道中的错误能被正确检测

# 获取脚本所在目录的绝对路径
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"

# 加载配置文件
CONFIG_FILE="$PROJECT_ROOT/config/config.sh"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo "✅ 已加载配置: $CONFIG_FILE"
else
    echo "❌ 错误：配置文件不存在: $CONFIG_FILE"
    echo "请复制 config/config.example.sh 为 config/config.sh 并填入你的配置"
    exit 1
fi

# 检查必需的环境变量
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ 错误：ANTHROPIC_API_KEY 未设置"
    echo "请在 config/config.sh 中配置你的 Claude API 密钥"
    exit 1
fi

SCRIPT_DIR="$SKILL_DIR"
CACHE_DIR="$SCRIPT_DIR/cache"
LOG_FILE="${LOG_FILE:-/var/log/ai-content.log}"
DATE=$(date +%Y-%m-%d)
OUTPUT_BASE_DIR="${OUTPUT_DIR:-$HOME/生成记录}"

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 网络检查函数
check_network() {
    log "检查网络连接..."

    # 测试DNS解析
    if ! nslookup baidu.com >/dev/null 2>&1; then
        log "❌ DNS解析失败"
        return 1
    fi

    # 测试网络连通性
    if ! curl -s --connect-timeout 5 --max-time 10 https://www.baidu.com >/dev/null 2>&1; then
        log "❌ 网络连接失败：无法访问外网"
        return 1
    fi

    log "✅ 网络连接正常"
    return 0
}

log "=== 开始AI内容自动发布流程 ==="

# 首先检查网络连接
if ! check_network; then
    log "❌ 网络检查失败，跳过本次执行"
    log "=== AI内容自动发布流程终止（网络问题） ==="
    exit 1
fi

# 进入脚本目录
cd "$SCRIPT_DIR"

# 创建输出目录（统一保存到生成记录目录）
OUTPUT_DIR="/home/ubuntu/生成记录/$DATE"
mkdir -p "$OUTPUT_DIR"

# 步骤1: 获取热点（带超时控制）
log "步骤1: 获取AI热点..."
if timeout 120 python3 scripts/fetch_hotspots.py 2>&1 | tee -a "$LOG_FILE"; then
    HOTSPOT_COUNT=$(python3 -c "import json; print(len(json.load(open('cache/hotspots.json'))))" 2>/dev/null || echo "0")
    log "✅ 热点获取成功，共 $HOTSPOT_COUNT 个热点"
else
    log "⚠️ 热点获取失败或超时，尝试使用缓存数据"
    if [ ! -f "cache/hotspots.json" ]; then
        log "❌ 无缓存数据，退出"
        exit 1
    fi
fi

# 步骤2: 选择选题
log "步骤2: 智能选题..."
if timeout 60 python3 scripts/selector.py 2>&1 | tee -a "$LOG_FILE"; then
    if [ -f "cache/selected_topic.json" ]; then
        TITLE=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json'))['title'])" 2>/dev/null || echo "")
        log "✅ 选题成功: $TITLE"
    else
        log "❌ 选题文件未生成"
        exit 1
    fi
else
    log "❌ 选题失败"
    exit 1
fi

# 步骤3: 生成标题
log "步骤3: 生成标题..."
GENERATED_TITLE=$(timeout 30 python3 -c "
import sys
sys.path.append('scripts')
from title_generator import generate_title
import json

topic = json.load(open('cache/selected_topic.json'))
content_type = topic.get('content_type', 'new_tool')
print(generate_title(topic, content_type))
" 2>&1)

if [ -n "$GENERATED_TITLE" ]; then
    log "✅ 标题生成: $GENERATED_TITLE"

    # 保存生成标题
    python3 -c "
import json
with open('cache/selected_topic.json', 'r') as f:
    topic = json.load(f)
topic['generated_title'] = '''$GENERATED_TITLE'''
with open('cache/selected_topic.json', 'w') as f:
    json.dump(topic, f, ensure_ascii=False, indent=2)
" 2>/dev/null
else
    log "❌ 标题生成失败"
    exit 1
fi

# 步骤4: 生成增强写作提示词并生成文章
log "步骤4: 生成增强写作提示词..."

# 读取选题详情
TOPIC_TITLE=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json'))['title'])" 2>/dev/null)
TOPIC_URL=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json'))['url'])" 2>/dev/null)
CONTENT_TYPE=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json')).get('content_type', 'new_tool'))" 2>/dev/null)

log "选题: $TOPIC_TITLE"
log "类型: $CONTENT_TYPE"

# 生成增强提示词
ENHANCED_PROMPT_FILE="$OUTPUT_DIR/enhanced_prompt.txt"
if python3 "$SCRIPT_DIR/scripts/generate_enhanced_prompt.py" \
    "$SCRIPT_DIR/cache/selected_topic.json" \
    "$CONTENT_TYPE" \
    > "$ENHANCED_PROMPT_FILE" 2>&1; then
    log "✅ 增强提示词生成完成"
else
    log "⚠️ 增强提示词生成失败，使用标准模式"
fi

# 使用增强提示词生成文章（带质量重试机制）
MAX_RETRIES=2
RETRY_COUNT=0
ARTICLE_PASSED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$ARTICLE_PASSED" = "false" ]; do
    if [ $RETRY_COUNT -gt 0 ]; then
        log "⚠️ 第 $RETRY_COUNT 次重试生成文章..."
    fi

    # 使用 wechat-tech-writer 的 generate.py 脚本生成文章
    GENERATE_LOG="$OUTPUT_DIR/generate.log"
    if python3 /home/ubuntu/wechat_article_skills/wechat-tech-writer/generate.py \
        --topic "$TOPIC_TITLE" \
        --url "$TOPIC_URL" \
        --type "$CONTENT_TYPE" \
        --output "$OUTPUT_DIR" \
        --mode standard 2>&1 | tee "$GENERATE_LOG" | tee -a "$LOG_FILE"; then

        # 验证文章文件确实生成且不为空
        ARTICLE_MD="$OUTPUT_DIR/article.md"
        if [ ! -f "$ARTICLE_MD" ]; then
            log "❌ 文章文件未生成: $ARTICLE_MD"
            log "📋 生成日志: $(tail -20 "$GENERATE_LOG" 2>&1)"
            RETRY_COUNT=$((RETRY_COUNT + 1))
            continue
        fi

        ARTICLE_SIZE=$(stat -c%s "$ARTICLE_MD" 2>/dev/null || echo "0")
        if [ "$ARTICLE_SIZE" -lt 100 ]; then
            log "❌ 文章文件为空或太小 (${ARTICLE_SIZE}字节)"
            log "📋 生成日志: $(tail -20 "$GENERATE_LOG" 2>&1)"
            RETRY_COUNT=$((RETRY_COUNT + 1))
            continue
        fi

        log "✅ 文章生成完成 (${ARTICLE_SIZE}字节)"

        # 步骤4.5: 质量检查
        log "步骤4.5: 文章质量检查..."

        # 查找生成的markdown文件
        MARKDOWN_FILE=$(find "$OUTPUT_DIR" -name "*.md" -type f -mmin -5 2>/dev/null | head -1)

        if [ -z "$MARKDOWN_FILE" ]; then
            MARKDOWN_FILE=$(find "$OUTPUT_DIR" -name "*.md" -type f 2>/dev/null | head -1)
        fi

        if [ -n "$MARKDOWN_FILE" ] && [ -f "$MARKDOWN_FILE" ]; then
            # 运行质量检查
            if python3 "$SCRIPT_DIR/scripts/article_quality_checker.py" "$MARKDOWN_FILE" 2>&1 | tee -a "$LOG_FILE"; then
                log "✅ 文章质量合格（评分≥70）"
                ARTICLE_PASSED=true
                break
            else
                log "❌ 文章质量不合格（评分<70）"
                RETRY_COUNT=$((RETRY_COUNT + 1))

                if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                    log "🔄 将重新生成文章..."
                    # 删除低质量文章
                    rm -f "$MARKDOWN_FILE"
                    sleep 3
                fi
            fi
        else
            log "❌ 未找到生成的文章文件"
            RETRY_COUNT=$((RETRY_COUNT + 1))
        fi
    else
        log "❌ 文章生成失败"
        RETRY_COUNT=$((RETRY_COUNT + 1))
    fi
done

if [ "$ARTICLE_PASSED" = "true" ]; then
    log "✅ 文章生成并通过质量检查"

    # 等待文件写入完成
    sleep 5

    # 步骤4.6: 从图片库选择封面图（强制要求，必须使用封面库）
    log "步骤4.6: 从图片库选择封面图..."
    if python3 scripts/select_cover.py "$CONTENT_TYPE" "$OUTPUT_DIR" 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ 封面图选择完成"
    else
        log "❌ 封面图选择失败！强制退出：必须使用封面库的图片"
        exit 1
    fi

    # 步骤5: 查找并格式化生成的文章
    log "步骤5: 格式化并发布文章..."

    # 查找生成的markdown文件
    MARKDOWN_FILE=$(find "$OUTPUT_DIR" -name "*.md" -type f -mmin -5 2>/dev/null | head -1)

    if [ -z "$MARKDOWN_FILE" ]; then
        log "⚠️ 未找到markdown文件，尝试查找任何生成的文件..."
        MARKDOWN_FILE=$(find "$OUTPUT_DIR" -name "*.md" -type f 2>/dev/null | head -1)
    fi

    if [ -n "$MARKDOWN_FILE" ] && [ -f "$MARKDOWN_FILE" ]; then
        log "📄 找到文章: $MARKDOWN_FILE"

        # 转换为HTML
        HTML_FILE="$OUTPUT_DIR/article_wechat.html"
        if timeout 60 python3 /home/ubuntu/.claude/skills/wechat-article-formatter/convert.py \
            "$MARKDOWN_FILE" \
            -o "$HTML_FILE" 2>&1 | tee -a "$LOG_FILE"; then

            log "✅ HTML格式化完成"

            # 查找封面图（必须从封面库选择）
            COVER_FILE="$OUTPUT_DIR/cover.png"
            if [ ! -f "$COVER_FILE" ]; then
                COVER_FILE=$(find "$OUTPUT_DIR" -name "cover.png" -type f 2>/dev/null | head -1)
            fi

            if [ ! -f "$COVER_FILE" ]; then
                log "❌ 封面图不存在！强制退出：必须使用封面库的图片"
                exit 1
            fi

            # 验证封面图是从封面库复制的（检查文件大小，封面库图片都>2MB）
            COVER_SIZE=$(stat -f%z "$COVER_FILE" 2>/dev/null || stat -c%s "$COVER_FILE" 2>/dev/null)
            if [ "$COVER_SIZE" -lt 2000000 ]; then
                log "❌ 封面图大小异常(${COVER_SIZE}字节)，不是从封面库选择的！强制退出"
                exit 1
            fi

            log "✅ 封面图验证通过: $COVER_FILE ($(ls -lh "$COVER_FILE" | awk '{print $5}'))"

            # 发布到草稿箱
            if timeout 60 python3 /home/ubuntu/.claude/skills/wechat-draft-publisher/publisher.py \
                --title "$GENERATED_TITLE" \
                --content "$HTML_FILE" \
                --cover "$COVER_FILE" \
                --author "阳桃AI干货" 2>&1 | tee -a "$LOG_FILE"; then

                log "✅ 发布到草稿箱成功"
            else
                log "❌ 发布到草稿箱失败"
            fi
        else
            log "❌ HTML格式化失败"
        fi
    else
        log "❌ 未找到生成的文章文件"
        log "📂 输出目录内容:"
        ls -la "$OUTPUT_DIR" 2>&1 | tee -a "$LOG_FILE" || true
    fi
else
    log "❌ 文章质量检查失败，已重试 $MAX_RETRIES 次仍未通过"
    log "💡 建议: 请检查写作模板配置或调整质量阈值"
    exit 1
fi

# 步骤6: 发布到小红书（新增双平台发布）
log "步骤6: 发布到小红书..."

# 准备小红书封面（使用精美封面库）
XHS_IMAGE_DIR="/home/ubuntu/xiaohongshu-mcp/docker/images"
XHS_IMAGE_NAME="xhs_cover_${DATE}.png"
XHS_IMAGE_PATH="$XHS_IMAGE_DIR/$XHS_IMAGE_NAME"

# 从精美封面库中选择封面（根据内容类型，强制要求）
log "从封面库选择精美封面..."
if python3 /home/ubuntu/.claude/skills/ai-content-publisher/scripts/select_cover.py "$CONTENT_TYPE" "$OUTPUT_DIR" 2>&1 | tee -a "$LOG_FILE"; then
    # 重新获取封面文件路径（select_cover.py会创建cover.png）
    COVER_FILE="$OUTPUT_DIR/cover.png"
    if [ -f "$COVER_FILE" ]; then
        log "✅ 精美封面已选择: $(basename "$COVER_FILE" | sed 's/cover.png/原文件/')"
    fi
else
    log "❌ 小红书封面选择失败！强制退出：必须使用封面库的图片"
    exit 1
fi

# 验证封面图文件存在且大小正常（封面库图片都>2MB）
if [ ! -f "$COVER_FILE" ]; then
    log "❌ 小红书封面文件不存在！强制退出"
    exit 1
fi

COVER_SIZE=$(stat -f%z "$COVER_FILE" 2>/dev/null || stat -c%s "$COVER_FILE" 2>/dev/null)
if [ "$COVER_SIZE" -lt 2000000 ]; then
    log "❌ 小红书封面图大小异常(${COVER_SIZE}字节)，不是从封面库选择的！强制退出"
    exit 1
fi

if [ -f "$COVER_FILE" ]; then
    # 复制封面图到Docker挂载目录
    if cp "$COVER_FILE" "$XHS_IMAGE_PATH"; then
        log "✅ 封面图已复制到小红书目录"
        log "   原始封面: $(ls -lh "$COVER_FILE" | awk '{print $5}')"

        # 生成小红书标题（≤20字）
        XHS_TITLE=$(python3 -c "
title = '''$GENERATED_TITLE'''
# 移除常见修饰词，保留核心关键词
import re
title = re.sub(r'[:：].*$', '', title)  # 删除冒号后内容
title = re.sub(r'[？?！!].*$', '', title)  # 删除问号感叹号后内容
title = title.strip()
# 直接截断到20字
if len(title) > 20:
    title = title[:20]
print(title)
" 2>&1)

        log "小红书标题: $XHS_TITLE"

        # 使用专用适配器生成小红书内容（≤1000字，emoji风格）
        XHS_CONTENT_FILE="$OUTPUT_DIR/xiaohongshu_content.txt"
        if python3 "$SCRIPT_DIR/scripts/adapt_for_xiaohongshu.py" \
            "$MARKDOWN_FILE" \
            "$XHS_CONTENT_FILE" 2>&1 | tee -a "$LOG_FILE"; then

            # 读取生成的小红书内容（只读取正文部分，跳过标题）
            XHS_CONTENT=$(tail -n +3 "$XHS_CONTENT_FILE" 2>/dev/null)

            if [ -z "$XHS_CONTENT" ]; then
                log "⚠️ 小红书内容为空，使用原始内容"
                XHS_CONTENT="$GENERATED_TITLE\n\n详情请访问公众号「阳桃AI干货」查看完整文章～"
            fi

            log "✅ 小红书内容生成完成"
            log "小红书内容长度: $(echo "$XHS_CONTENT" | wc -c)字"
        else
            log "⚠️ 小红书内容适配失败，使用简化版"
            XHS_CONTENT="🔥 分享个AI好工具！\n\n详情请访问公众号「阳桃AI干货」查看完整文章～\n\n💬 觉得有用记得点赞收藏！"
        fi

        # 发布到小红书（使用 Python JSON 编码处理特殊字符）
        log "正在发布到小红书..."
        XHS_RESPONSE=$(python3 -c "
import json
import sys
import urllib.request
import urllib.error

try:
    # 读取小红书内容文件
    with open('$XHS_CONTENT_FILE', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 跳过前2行（标题行和空行）
        content = ''.join(lines[2:]).strip()

    # 如果内容为空，使用fallback
    if not content:
        content = '详情请访问公众号「阳桃AI干货」查看完整文章～'

    # 构造payload
    payload = {
        'title': '''$XHS_TITLE''',
        'content': content,
        'images': ['/app/images/$XHS_IMAGE_NAME'],
        'tags': ['AI', '科技']
    }

    # 发送请求
    req = urllib.request.Request(
        'http://localhost:18060/api/v1/publish',
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        result = response.read().decode('utf-8')
        print(result)

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(json.dumps({'success': False, 'error': f'HTTP {e.code}: {error_body}'}))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
" 2>&1)

        # 检查发布结果
        if echo "$XHS_RESPONSE" | grep -q '"success":true'; then
            log "✅ 小红书发布成功"
        else
            log "⚠️ 小红书发布失败: $XHS_RESPONSE"
        fi
    else
        log "⚠️ 封面图复制失败，跳过小红书发布"
    fi
else
    log "⚠️ 未找到封面图，跳过小红书发布"
fi

# 步骤8: 更新发布历史
log "步骤8: 更新发布历史..."
if python3 "$SCRIPT_DIR/scripts/update_history.py" \
    "$CACHE_DIR/selected_topic.json" \
    "$GENERATED_TITLE" 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ 历史记录已更新"
else
    log "⚠️  历史记录更新失败（不影响发布）"
fi

log "=== AI内容自动发布流程完成（双平台） ==="
