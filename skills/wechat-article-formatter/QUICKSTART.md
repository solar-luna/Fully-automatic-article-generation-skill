# 快速参考卡 - WeChat Article Formatter

**3 分钟快速上手指南**

---

## 🚀 最快速的使用方式

### 单行命令（最常用）

```bash
cd /root/.claude/skills/wechat-article-formatter
python scripts/markdown_to_html.py --input article.md --theme tech --preview
```

**效果**：
- ✅ 转换 Markdown 为 HTML
- ✅ 应用科技风主题
- ✅ 自动在浏览器打开预览

---

## 🎨 主题选择（3 秒决策）

| 文章类型 | 主题 | 命令 |
|---------|------|------|
| 技术文章/编程/AI | `tech` | `--theme tech` |
| 生活/读书/通用 | `minimal` | `--theme minimal` |
| 商业/数据/报告 | `business` | `--theme business` |

---

## 📋 完整工作流（2 分钟）

```bash
# 1. 进入目录
cd /root/.claude/skills/wechat-article-formatter

# 2. 转换
python scripts/markdown_to_html.py \
  --input "你的文章.md" \
  --theme tech \
  --preview

# 3. 浏览器会自动打开预览

# 4. 复制粘贴到微信公众号
# Ctrl+A → Ctrl+C → 粘贴到微信编辑器 → 发布
```

---

## 🔄 与 wechat-tech-writer 配合

**场景**：刚用 wechat-tech-writer 生成了文章

```bash
# 自动查找最新文章并转换
latest=$(ls -t *.md | head -1)
python scripts/markdown_to_html.py --input "$latest" --theme tech --preview
```

---

## ❌ 常见问题（5 秒解决）

| 问题 | 解决方案 |
|------|---------|
| 代码块没高亮 | Markdown 中用 \`\`\`python（指定语言） |
| 粘贴后样式丢失 | 用"粘贴"不要用"粘贴并匹配样式" |
| 图片显示不了 | 在微信编辑器重新上传图片 |
| 表格太宽 | 减少列数（≤4列）或接受横向滚动 |

---

## 🔧 高级用法

### 批量转换

```bash
python scripts/batch_convert.py --input articles/ --theme minimal --workers 8
```

### 实时预览

```bash
python scripts/preview_generator.py --input article.md --theme business
```

### 自定义主题

```bash
# 1. 复制现有主题
cp templates/tech-theme.css templates/my-theme.css

# 2. 编辑颜色
# 修改 my-theme.css

# 3. 使用
python scripts/markdown_to_html.py --input article.md --theme my
```

---

## 📖 需要更多帮助？

- **SKILL.md** - Claude 执行指南（详细步骤）
- **README.md** - 完整功能说明
- **EXAMPLES.md** - 3 个实战示例
- **references/** - 详细技术文档

---

**记住核心**：Markdown → 一键转换 → 复制粘贴 → 发布（2 分钟）
