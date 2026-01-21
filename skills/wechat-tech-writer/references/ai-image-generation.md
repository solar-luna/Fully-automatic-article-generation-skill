# AI图片生成指南

## 概述

AI生成图片可以有效补充技术文章的视觉内容，特别适合创建封面图、概念示意图和场景插画。

**重要更新**：现在支持**直接调用生图API**生成真实图片并嵌入文章，而不仅仅是提供提示词！

## ⚠️ 重要优化原则（2025-12-27更新）

### 1. 图片文字必须使用中文
- **所有图片上的文字都必须使用简体中文**
- 文字数量要少，只保留关键信息
- 文字必须准确无误，不能出现错别字或拼写错误
- 在提示词中明确要求："text in simplified Chinese, minimal text, accurate and clear"

### 2. 只生成真正必要的图片
**必要图片的判断标准**：
- ✅ **性能对比图**：有明确的数据对比时必须生成
- ✅ **技术架构图**：涉及复杂技术原理需要可视化时生成
- ✅ **封面图**：可选，仅在需要吸引眼球时生成
- ❌ **装饰性配图**：不要生成纯装饰性的图片
- ❌ **场景插画**：除非对理解内容有实质帮助，否则不生成

**生成决策流程**：
1. 阅读文章内容
2. 判断是否有数据对比 → 是：生成对比图
3. 判断是否有复杂技术 → 是：生成架构图
4. 判断是否需要封面 → 视情况决定
5. 其他图片一律不生成

**典型场景**：
- 产品评测文章：生成1-2张（封面图 + 性能对比图）
- 技术解析文章：生成1-2张（技术架构图 + 可选封面图）
- 新闻资讯文章：生成0-1张（可选封面图）

### 3. 图片数量控制
- 每篇文章图片数量：**1-3张**（之前是4-6张）
- 优先级：数据图 > 架构图 > 封面图 > 其他
- 宁缺毋滥，质量优于数量

## 🚀 快速开始：调用生图API

### 方式一：使用脚本调用外部API

使用 `scripts/generate_image.py` 脚本可以直接调用Gemini或DALL-E API：

**基本用法**：
```bash
# 使用Gemini Imagen API (推荐)
python scripts/generate_image.py \
  --prompt "图片描述提示词" \
  --api gemini \
  --output /home/claude/images/cover.png

# 使用DALL-E API (OpenAI)
python scripts/generate_image.py \
  --prompt "图片描述提示词" \
  --api dalle \
  --output /home/claude/images/cover.png
```

**环境配置**：
```bash
# 使用Gemini需要设置
export GEMINI_API_KEY="your-api-key"

# 使用DALL-E需要设置
export OPENAI_API_KEY="your-api-key"
```

**完整示例**：
```python
import subprocess
import os

# 生成封面图
subprocess.run([
    'python', 'scripts/generate_image.py',
    '--prompt', 'A modern cover image for an article about Claude AI. Style: minimalist, blue gradient.',
    '--api', 'gemini',
    '--output', '/home/claude/images/cover.png'
])

# 检查图片是否生成成功
if os.path.exists('/home/claude/images/cover.png'):
    print("✅ 封面图生成成功")
```

### 方式二：在claude.ai中使用Claude原生能力

如果在claude.ai环境中，可以直接使用Claude的图片生成能力（无需外部API）：

```markdown
请根据以下描述生成一张图片：
A modern cover image for an article about Claude AI.
Style: minimalist, professional, gradient blue background.
```

Claude会直接生成图片，然后保存到本地并在文章中引用。

### 支持的API对比

| API | 优势 | 劣势 | 推荐场景 |
|-----|------|------|---------|
| **Gemini Imagen** | 质量高，速度快，价格合理 | 需要Google API密钥 | 所有场景，首选 |
| **DALL-E 3** | 质量优秀，细节丰富 | 速度较慢，价格稍高 | 需要高质量封面图 |
| **Claude原生** | 无需外部API，方便 | 仅在claude.ai可用 | claude.ai环境 |

## 工作流集成

在文章生成流程中，图片生成步骤如下：

```python
# 1. 确定需要的图片类型和提示词
images_to_generate = [
    {
        "type": "cover",
        "prompt": "封面图提示词",
        "output": "/home/claude/images/cover.png"
    },
    {
        "type": "concept",
        "prompt": "概念图提示词",
        "output": "/home/claude/images/concept.png"
    },
    {
        "type": "scene",
        "prompt": "场景图提示词",
        "output": "/home/claude/images/scene.png"
    }
]

# 2. 批量生成图片
for img in images_to_generate:
    subprocess.run([
        'python', 'scripts/generate_image.py',
        '--prompt', img['prompt'],
        '--api', 'gemini',
        '--output', img['output']
    ])

# 3. 在文章中嵌入生成的图片
article = f"""
# 文章标题

![封面图]({images_to_generate[0]['output']})

## 核心概念

![概念图]({images_to_generate[1]['output']})

## 应用场景

![场景图]({images_to_generate[2]['output']})
"""

# 4. 将图片复制到输出目录
import shutil
for img in images_to_generate:
    shutil.copy(img['output'], '/mnt/user-data/outputs/')
```

---

## 何时使用AI生成图片

### ✅ 适合AI生成的场景

1. **封面图/首图**
   - 吸引读者点击的视觉设计
   - 体现文章主题的创意图
   - 品牌风格的标题图

2. **概念示意图**
   - 抽象技术概念的可视化
   - 工作流程的示意图
   - 系统架构的简化表现

3. **场景插画**
   - 使用场景的情景化展示
   - 问题场景的描绘
   - 解决方案的效果展示

4. **对比示意图**
   - 功能对比的视觉化
   - 使用前后的对比
   - 不同方案的比较

5. **装饰性配图**
   - 段落间的视觉分隔
   - 增强阅读体验的插图
   - 主题相关的背景图

### ❌ 不适合AI生成的场景

1. **实际产品截图**
   - 软件界面必须用真实截图
   - 代码编辑器画面
   - 实际操作步骤

2. **真实数据图表**
   - 性能测试数据
   - 市场占有率图表
   - GitHub Star趋势图

3. **官方品牌素材**
   - 产品Logo
   - 官方宣传图
   - 品牌标识

4. **技术细节图**
   - 复杂的架构图（需要准确性）
   - 详细的流程图
   - 代码结构图

## 技术文章的图片风格建议

### 整体风格原则

**推荐风格**：
- 🎨 **现代简约** - 干净、专业
- 🎯 **科技感** - 体现技术主题
- 📊 **信息清晰** - 易于理解
- 🌈 **色彩统一** - 全文风格一致

**避免的风格**：
- ❌ 过于卡通或幼稚
- ❌ 过度复杂或花哨
- ❌ 色彩杂乱无章
- ❌ 与技术主题无关

### 配色建议

**科技蓝色系**（适合AI、云计算、开发工具）：
- 主色：深蓝 #1a73e8、科技蓝 #4285f4
- 辅色：浅蓝 #e8f4ff、白色 #ffffff
- 点缀：橙色 #ff6b35（用于强调）

**紫色渐变系**（适合AI、创新工具）：
- 主色：深紫 #6366f1、亮紫 #a78bfa
- 辅色：浅紫 #f5f3ff、白色
- 点缀：粉色 #ec4899

**绿色系**（适合数据、性能、效率）：
- 主色：深绿 #059669、亮绿 #10b981
- 辅色：浅绿 #d1fae5、白色
- 点缀：黄色 #fbbf24

**黑白灰系**（适合严肃、专业内容）：
- 主色：深灰 #1f2937、黑色 #000000
- 辅色：浅灰 #f3f4f6、白色
- 点缀：蓝色或绿色

## 不同类型图片的提示词模板

### 1. 封面图/首图

**目标**：吸引眼球，传达文章主题

**提示词模板**：
```
A modern, clean cover image for a tech article about [主题].
Style: minimalist, professional, tech-focused.
Color scheme: [蓝色/紫色/绿色] gradient background.
Elements: [关键元素，如AI brain, code symbols, cloud icons, etc.]
Text: minimal text in simplified Chinese only, accurate and clear.
Composition: centered, with copy space for title text.
High quality, 16:9 aspect ratio.
```

**⚠️ 中文文字要求**：
- 所有提示词必须包含："text in simplified Chinese, minimal text, accurate"
- 图片上的文字要少而精，仅保留核心信息
- 避免复杂长句，使用简短词汇

**具体示例**：

**示例1 - AI模型文章封面**：
```
A modern, clean cover image for a tech article about Claude AI assistant.
Style: minimalist, professional, futuristic.
Color scheme: gradient from deep blue (#1a73e8) to light blue (#e8f4ff).
Elements: abstract AI neural network visualization, glowing nodes and connections, subtle circuit patterns in background.
Composition: centered abstract design with space at top for article title.
Mood: innovative, intelligent, approachable.
High quality, 16:9 aspect ratio, professional tech illustration.
```

**示例2 - 开源工具封面**：
```
A modern cover image for an article about LangChain framework.
Style: clean, professional, developer-focused.
Color scheme: dark background (#1f2937) with bright green (#10b981) and blue (#4285f4) accents.
Elements: connected chain links representing workflow, code brackets, small icons of tools/modules.
Composition: horizontal layout with geometric shapes, space for title on left.
Mood: powerful, flexible, interconnected.
High quality, 16:9 aspect ratio.
```

### 2. 概念示意图

**目标**：可视化抽象概念，帮助理解

**提示词模板**：
```
A simple, clear diagram illustrating [概念/原理].
Style: infographic, clean lines, minimal text.
Color scheme: [2-3种颜色].
Elements: [具体元素，如arrows, boxes, icons].
Layout: [flow chart / circular / hierarchical].
Professional, easy to understand, tech illustration style.
```

**具体示例**：

**示例1 - 工作流程图**：
```
A clean diagram showing how LangChain processes user requests.
Style: flowchart with rounded boxes and arrows, modern infographic style.
Color scheme: white background, blue boxes (#4285f4), green success arrows (#10b981), orange highlights (#ff6b35).
Elements: 4-5 connected steps from left to right - User Input → LLM Processing → Tool Integration → Response Output.
Include simple icons in each box (message icon, brain icon, tools icon, checkmark).
Clean, professional, easy to read, tech documentation style.
Aspect ratio: 16:9, horizontal layout.
```

**示例2 - 架构示意图**：
```
A simplified architecture diagram showing three-tier application structure.
Style: modern technical illustration, isometric or flat design.
Color scheme: dark blue background (#1a73e8), white/light blue components.
Elements: three distinct layers (Frontend, Backend, Database) represented as boxes or platforms, with bidirectional arrows showing data flow.
Include minimal icons (browser, server, database symbols).
Clean, professional, suitable for tech documentation.
No text labels needed - keep it visual.
Aspect ratio: 16:9 or 1:1.
```

### 3. 场景插画

**目标**：展示实际应用场景，增加代入感

**提示词模板**：
```
An illustration showing [使用场景].
Style: modern flat design / isometric illustration.
Color scheme: [温暖/科技感的配色].
Characters: [可选：简化的人物剪影].
Environment: [办公室/家庭/移动场景].
Mood: [productive / innovative / user-friendly].
Clean, professional, tech article illustration.
```

**具体示例**：

**示例1 - 开发者使用场景**：
```
An illustration of a developer using AI coding assistant at desk.
Style: modern flat design illustration, simple and clean.
Color scheme: purple gradient background (#6366f1 to #a78bfa), white desk, laptop.
Scene: minimalist home office setup, developer silhouette facing laptop, subtle AI sparkles/glow from screen.
Mood: focused, productive, empowered by technology.
No facial details needed - keep it simple and professional.
Aspect ratio: 16:9, horizontal composition.
```

**示例2 - 多设备使用场景**：
```
An isometric illustration showing cross-platform application usage.
Style: clean isometric design, tech-focused.
Color scheme: light background with blue (#4285f4) and green (#10b981) device screens.
Elements: smartphone, tablet, laptop arranged in a connected layout, subtle data flow lines between devices.
Mood: connected, seamless, modern.
Professional tech illustration, minimal details.
Aspect ratio: 1:1 or 16:9.
```

### 4. 对比示意图

**目标**：清晰展示差异或改进

**提示词模板**：
```
A before/after or comparison illustration showing [对比内容].
Style: split-screen or side-by-side layout.
Color scheme: [左侧/before用暗色或红色，右侧/after用亮色或绿色].
Elements: clearly distinguishable visual differences.
Labels: minimal, use visual cues like ✗ and ✓.
Professional comparison infographic style.
```

**具体示例**：

**示例1 - 性能对比**：
```
A split-screen comparison: slow process vs fast process.
Style: minimalist infographic, clear visual contrast.
Color scheme: left side - gray/red tones showing slowness, right side - green/blue showing speed.
Left: loading spinner, progress bar at 30%, clock showing long time.
Right: checkmark, completed progress bar, clock showing short time.
Include simple speed indicators: tortoise icon left, rocket icon right.
Clean, professional, no text needed - purely visual.
Aspect ratio: 16:9, equal split down the middle.
```

**示例2 - 功能对比**：
```
A side-by-side comparison of limited features vs full features.
Style: modern infographic, checklist visual.
Color scheme: white background, left boxes in gray with red ✗, right boxes in blue with green ✓.
Layout: 2 columns, 5 rows of feature boxes showing contrast.
Keep it abstract - use icons and checkmarks instead of text.
Professional, clean, tech comparison chart style.
Aspect ratio: 9:16 vertical or 1:1 square.
```

### 5. 装饰性配图

**目标**：美化排版，提升视觉体验

**提示词模板**：
```
An abstract, decorative background for [主题] section.
Style: subtle, non-distracting, modern.
Color scheme: [柔和的渐变或单色].
Elements: [几何图形/流线/粒子效果].
Mood: professional, calm, tech-related.
Can be used as section divider or background.
```

**具体示例**：

**示例1 - 段落分隔图**：
```
An abstract tech-themed divider image.
Style: minimalist geometric design, horizontal orientation.
Color scheme: gradient from blue (#1a73e8) to purple (#6366f1).
Elements: flowing lines, subtle circuit patterns, small glowing dots.
Composition: horizontal banner, very subtle and not distracting.
Can be used between article sections.
Aspect ratio: 21:9 ultra-wide, very flat.
Professional, modern, suitable for tech blog.
```

**示例2 - 背景纹理**：
```
A subtle tech pattern background.
Style: minimalist, repeating pattern or gradient.
Color scheme: very light - soft blue (#e8f4ff) to white, or light gray (#f3f4f6).
Elements: faint grid lines, tiny dots, or subtle geometric shapes.
Very low contrast - should not distract from text.
Suitable as section background in article.
Seamless, tileable pattern.
High quality but subtle presence.
```

## 风格统一性建议

为确保全文图片风格一致：

### 1. 确定主色调

在开始生成前，选择一个主色调贯穿全文：
- **AI/大模型文章**：蓝紫色系
- **开发工具文章**：蓝绿色系
- **性能/数据文章**：绿色系
- **企业级工具**：黑灰蓝色系

### 2. 统一设计风格

整篇文章选择一种风格并坚持：
- **扁平化设计** (Flat Design)
- **等距插画** (Isometric)
- **渐变风格** (Gradient)
- **极简主义** (Minimalist)

### 3. 一致的复杂度

- 如果封面用简约风格，其他图也要简约
- 避免一张图很复杂，另一张很简单
- 保持视觉密度的一致性

### 4. 统一的提示词要素

在每个提示词中重复这些要素：
```
Style: [统一的风格描述]
Color scheme: [统一的配色]
Mood: professional, modern, tech-focused
Quality: high quality, clean, suitable for tech article
```

## 图片生成工作流

### Step 1: 规划图片需求

阅读完成的文章草稿，列出需要的图片：

**示例规划表**：
```
1. 封面图 - 主题：Claude AI - 类型：封面 - 风格：科技蓝
2. 概念图 - 展示：工作原理 - 类型：流程图 - 风格：科技蓝
3. 场景图 - 展示：使用场景 - 类型：插画 - 风格：科技蓝
4. 对比图 - 展示：性能提升 - 类型：对比 - 风格：科技蓝
```

### Step 2: 选择主色调和风格

基于文章主题选择：
- 主色调：例如 科技蓝 (#1a73e8, #4285f4, #e8f4ff)
- 设计风格：例如 现代扁平化设计
- 情绪基调：专业、创新、易用

### Step 3: 编写统一的提示词

为每张图编写提示词，确保包含统一要素：

**提示词检查清单**：
- [ ] 明确了图片类型和内容
- [ ] 指定了统一的风格
- [ ] 使用了统一的配色方案
- [ ] 说明了构图和比例
- [ ] 标注了质量要求
- [ ] 确保了与主题的相关性

### Step 4: 生成并检查

生成后检查：
- ✅ 风格是否一致
- ✅ 色调是否协调
- ✅ 清晰度是否足够
- ✅ 是否与内容相关
- ✅ 是否适合公众号排版

### Step 5: 嵌入文章并标注

在文章中嵌入图片时：
```markdown
![图1：Claude AI工作原理示意图](image_url)
*AI生成图片：展示Claude的核心工作流程*
```

## 提示词优化技巧

### 1. 具体而非抽象

❌ "A nice tech image"
✅ "A clean infographic showing data flow with blue arrows on white background"

### 2. 描述风格参考

❌ "Modern style"
✅ "Modern flat design illustration, similar to tech blog graphics, professional and clean"

### 3. 明确构图

❌ "Some icons"
✅ "Three icons arranged horizontally in the center, equal spacing, on gradient background"

### 4. 控制复杂度

❌ "Complex system architecture"
✅ "Simplified 3-tier architecture with 3 main components and connecting arrows"

### 5. 指定情绪和氛围

❌ "Tech background"
✅ "Tech background with mood: innovative, trustworthy, user-friendly"

## 常见问题处理

### Q: 生成的图片太复杂了怎么办？

A: 在提示词中强调：
- "minimalist"
- "simple"
- "clean design"
- "maximum 5 elements"

### Q: 颜色不够统一？

A: 明确指定颜色代码：
- "Color scheme: only use #1a73e8 (blue), #ffffff (white), and #000000 (black)"

### Q: 图片和文章主题不搭？

A: 在提示词开头明确主题：
- "For an article about [具体主题]..."
- "In the context of [技术领域]..."

### Q: 风格不够专业？

A: 添加质量描述词：
- "professional tech illustration"
- "suitable for enterprise blog"
- "high-quality documentation style"

## 输出格式示例

在文章中整合AI生成图片时的格式：

```markdown
## 核心功能

Claude Sonnet 4拥有强大的多模态理解能力：

![图1：Claude多模态处理能力示意图](image_url)
*AI生成概念图：展示Claude如何同时处理文本、图片和文档*

如上图所示，Claude可以...

---

## 文章配图列表

### 真实截图（来自官方/网络）
1. **GitHub仓库首页**
   - 来源：抓取自官方
   - 图片URL: https://...
   
### AI生成图片
1. **封面图**
   - 类型：AI生成
   - 主题：Claude AI助手
   - 风格：科技蓝渐变，现代简约
   - 用途：文章开头
   
2. **工作原理图**
   - 类型：AI生成
   - 内容：多模态处理流程
   - 风格：蓝色信息图
   - 用途："核心功能"部分

3. **应用场景图**
   - 类型：AI生成
   - 内容：开发者使用场景
   - 风格：扁平化插画
   - 用途："使用场景"部分
```

## 最佳实践总结

1. ✅ **混合使用**：真实截图 + AI生成图，各取所长
2. ✅ **提前规划**：先确定需要哪些图，再统一生成
3. ✅ **风格统一**：全文使用相同的色系和风格
4. ✅ **简约优先**：技术文章配图宜简不宜繁
5. ✅ **标注来源**：清楚标明哪些是AI生成
6. ✅ **质量检查**：生成后检查清晰度和相关性
7. ✅ **适度装饰**：不要为了配图而配图

通过合理使用AI生成图片，可以让技术文章更加生动专业，同时保持高效的创作流程！
