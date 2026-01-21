#!/bin/bash
# AI内容自动发布 - 手动测试脚本
# 效果和定时任务完全一样，只是方便你手动执行

set -e

SCRIPT_DIR="/home/ubuntu/.claude/skills/ai-content-publisher"
LOG_FILE="$HOME/ai-content-manual.log"
DATE=$(date +%Y-%m-%d)

# 记录日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== 手动触发AI内容自动发布流程 ==="

# 进入脚本目录
cd "$SCRIPT_DIR"

# 创建输出目录
OUTPUT_DIR="$SCRIPT_DIR/output/$DATE/article"
mkdir -p "$OUTPUT_DIR"

# 步骤1: 获取热点
log "步骤1: 获取AI热点..."
if timeout 120 python3 scripts/fetch_hotspots.py 2>&1 | tee -a "$LOG_FILE"; then
    HOTSPOT_COUNT=$(python3 -c "import json; print(len(json.load(open('cache/hotspots.json'))))" 2>/dev/null || echo "0")
    log "✅ 热点获取成功，共 $HOTSPOT_COUNT 个热点"
else
    log "❌ 热点获取失败"
    exit 1
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

# 读取选题详情
TOPIC_TITLE=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json'))['title'])" 2>/dev/null)
TOPIC_URL=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json'))['url'])" 2>/dev/null)
CONTENT_TYPE=$(python3 -c "import json; print(json.load(open('cache/selected_topic.json')).get('content_type', 'new_tool'))" 2>/dev/null)

log "选题: $TOPIC_TITLE"
log "类型: $CONTENT_TYPE"

# 步骤4: 调用 wechat-tech-writer 生成文章
log "步骤4: 调用 wechat-tech-writer 生成文章..."
if python3 /home/ubuntu/wechat_article_skills/wechat-tech-writer/generate.py \
    --topic "$TOPIC_TITLE" \
    --url "$TOPIC_URL" \
    --type "$CONTENT_TYPE" \
    --output "$OUTPUT_DIR" \
    --mode standard 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ 文章生成完成"

    # 等待文件写入完成
    sleep 5

    # 步骤4.5: 从图片库选择封面图
    log "步骤4.5: 从图片库选择封面图..."
    if python3 scripts/select_cover.py "$CONTENT_TYPE" "$OUTPUT_DIR" 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ 封面图选择完成"
    else
        log "⚠️ 封面图选择失败，使用AI生成的图片"
    fi

    # 步骤5: 格式化并发布
    log "步骤5: 格式化并发布文章..."

    # 查找生成的markdown文件
    MARKDOWN_FILE=$(find "$OUTPUT_DIR" -name "*.md" -type f 2>/dev/null | head -1)

    if [ -n "$MARKDOWN_FILE" ] && [ -f "$MARKDOWN_FILE" ]; then
        log "📄 找到文章: $MARKDOWN_FILE"

        # 转换为HTML
        HTML_FILE="$OUTPUT_DIR/article_wechat.html"
        if timeout 60 python3 /home/ubuntu/wechat_article_skills/wechat-article-formatter/scripts/markdown_to_html.py \
            --input "$MARKDOWN_FILE" \
            --theme tech \
            --output "$HTML_FILE" 2>&1 | tee -a "$LOG_FILE"; then

            log "✅ HTML格式化完成"

            # 查找封面图
            COVER_FILE="$OUTPUT_DIR/cover.png"
            if [ ! -f "$COVER_FILE" ]; then
                COVER_FILE=$(find "$OUTPUT_DIR" -name "cover.png" -type f 2>/dev/null | head -1)
            fi

            if [ -f "$COVER_FILE" ]; then
                # 发布到草稿箱
                if timeout 60 python3 /home/ubuntu/wechat_article_skills/wechat-draft-publisher/publisher.py \
                    --title "$GENERATED_TITLE" \
                    --content "$HTML_FILE" \
                    --cover "$COVER_FILE" \
                    --author "阳桃AI干货" 2>&1 | tee -a "$LOG_FILE"; then

                    log "✅ 发布到草稿箱成功"
                else
                    log "❌ 发布到草稿箱失败"
                fi
            else
                log "❌ 未找到封面图: $COVER_FILE"
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
    log "❌ 文章生成失败"
    exit 1
fi

log "=== AI内容自动发布流程完成 ==="
echo ""
echo "📱 请前往微信公众号后台查看草稿："
echo "https://mp.weixin.qq.com"
