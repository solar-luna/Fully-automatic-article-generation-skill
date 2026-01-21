#!/bin/bash
# 快速测试脚本 - 验证核心功能是否工作

SCRIPT_DIR="/home/ubuntu/.claude/skills/ai-content-publisher"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "快速测试：AI内容发布系统优化"
echo "=========================================="
echo ""

# 1. 测试选题（如果有热点数据）
if [ -f "cache/hotspots.json" ]; then
    echo "1️⃣ 测试智能选题（去重+实用性+多样性）..."
    echo ""
    python3 scripts/selector.py
    echo ""
    echo "✅ 选题测试完成"
    echo ""
else
    echo "⚠️  跳过选题测试（需要先运行 fetch_hotspots.py）"
    echo ""
fi

# 2. 测试标题生成
if [ -f "cache/selected_topic.json" ]; then
    echo "2️⃣ 测试标题生成（A/B测试）..."
    echo ""
    TITLE=$(python3 -c "
import sys
import json
sys.path.append('scripts')
from title_generator import generate_title

with open('cache/selected_topic.json', 'r') as f:
    topic = json.load(f)

content_type = topic.get('content_type', 'new_tool')
title = generate_title(topic, content_type)
print(title)
")
    echo "生成的标题: $TITLE"
    echo ""
    echo "✅ 标题生成测试完成"
    echo ""
else
    echo "⚠️  跳过标题测试（需要先运行选题）"
    echo ""
fi

# 3. 测试增强提示词
if [ -f "cache/selected_topic.json" ]; then
    echo "3️⃣ 测试增强提示词生成..."
    echo ""
    python3 scripts/generate_enhanced_prompt.py cache/selected_topic.json new_tool | head -30
    echo "..."
    echo ""
    echo "✅ 增强提示词测试完成"
    echo ""
fi

# 4. 测试质量评分（使用README作为示例）
if [ -f "README.md" ]; then
    echo "4️⃣ 测试文章质量评分系统..."
    echo ""
    python3 scripts/article_quality_checker.py README.md | tail -15
    echo ""
    echo "✅ 质量评分测试完成"
    echo ""
fi

# 5. 测试小红书适配
if [ -f "README.md" ]; then
    echo "5️⃣ 测试小红书内容适配器..."
    echo ""
    python3 scripts/adapt_for_xiaohongshu.py README.md /tmp/xhs_test.txt
    echo ""
    echo "生成的小红书内容:"
    echo "----------------------------------------"
    cat /tmp/xhs_test.txt
    echo "----------------------------------------"
    echo ""
    echo "✅ 小红书适配测试完成"
    echo ""
fi

echo "=========================================="
echo "✅ 快速测试完成！"
echo "=========================================="
echo ""
echo "如需完整测试，请运行："
echo "  ./test_optimizations.sh"
echo ""
echo "如需运行完整流程，请运行："
echo "  ./auto_publish.sh"
echo ""
