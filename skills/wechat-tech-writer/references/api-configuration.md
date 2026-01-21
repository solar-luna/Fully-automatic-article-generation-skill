# API配置指南

本文档说明如何配置生图API密钥，以便skill能够直接调用API生成图片。

## 支持的生图API

目前skill支持以下生图API：

1. **Gemini Imagen API** (Google) - 推荐
2. **DALL-E 3 API** (OpenAI)
3. **Claude原生** (仅在claude.ai环境中)

## 配置步骤

### 方式一：Gemini Imagen API (推荐)

#### 1. 获取API密钥

访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取API密钥。

#### 2. 设置环境变量

在使用前，需要设置环境变量：

**Linux/Mac**:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

**Windows (PowerShell)**:
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key-here"
```

**在Claude中设置** (如果Claude环境支持):
```python
import os
os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key-here'
```

#### 3. 测试配置

```bash
python scripts/generate_image.py \
  --prompt "A simple blue gradient background" \
  --api gemini \
  --output test.png
```

如果看到 `✅ 图片已生成: test.png`，说明配置成功！

#### 价格参考

- Imagen 3.0: 约 $0.04 per image (标准质量)
- 比DALL-E更实惠

### 方式二：DALL-E API (OpenAI)

#### 1. 获取API密钥

访问 [OpenAI Platform](https://platform.openai.com/api-keys) 创建API密钥。

#### 2. 设置环境变量

**Linux/Mac**:
```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
```

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="sk-your-openai-api-key"
```

**在Claude中设置**:
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-openai-api-key'
```

#### 3. 测试配置

```bash
python scripts/generate_image.py \
  --prompt "A simple blue gradient background" \
  --api dalle \
  --quality standard \
  --output test.png
```

#### 价格参考

- DALL-E 3 标准质量: $0.04 per image (1024x1024)
- DALL-E 3 HD质量: $0.08 per image (1024x1024)
- 更大尺寸价格更高

### 方式三：Claude原生 (仅claude.ai)

如果你在claude.ai环境中使用，可以直接使用Claude的图片生成能力，无需额外配置：

```python
# 在claude.ai中，直接请求生成图片
# Claude会使用原生能力生成
```

不需要设置任何API密钥。

## 在Skill中使用

### 自动检测可用API

Skill会按以下优先级自动选择可用的API：

1. 检查 `GEMINI_API_KEY` 是否设置 → 使用Gemini
2. 检查 `OPENAI_API_KEY` 是否设置 → 使用DALL-E
3. 如果在claude.ai环境 → 使用Claude原生
4. 如果都不可用 → 提供提示词，不生成真实图片

### 手动指定API

你也可以在请求时指定使用哪个API：

```
写一篇关于XXX的文章，使用Gemini API生成图片
```

或

```
写一篇关于XXX的文章，使用DALL-E生成图片
```

## 成本估算

假设一篇文章需要生成4张AI图片：

| API | 单张价格 | 4张总价 | 质量 | 速度 |
|-----|---------|---------|------|------|
| Gemini Imagen | ~$0.04 | ~$0.16 | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| DALL-E 3 标准 | $0.04 | $0.16 | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| DALL-E 3 HD | $0.08 | $0.32 | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| Claude原生 | 免费* | 免费* | ⭐⭐⭐⭐ | ⚡⚡⚡ |

*Claude原生功能可能受订阅计划限制

## 常见问题

### Q: 如何查看我的API配额？

**Gemini**:
- 访问 [Google AI Studio](https://aistudio.google.com/)
- 查看"Quotas"标签页

**DALL-E**:
- 访问 [OpenAI Usage Dashboard](https://platform.openai.com/usage)

### Q: API调用失败怎么办？

1. **检查API密钥是否正确**
   ```bash
   echo $GEMINI_API_KEY  # 或 $OPENAI_API_KEY
   ```

2. **查看错误信息**
   脚本会显示详细的错误信息，如：
   - `401 Unauthorized` → API密钥无效
   - `429 Too Many Requests` → 超过配额限制
   - `503 Service Unavailable` → API服务暂时不可用

3. **降级方案**
   如果API不可用，skill会自动降级为仅提供提示词模式。

### Q: 可以使用其他生图API吗？

可以！你可以修改 `scripts/generate_image.py` 添加其他API支持，如：
- Stability AI (Stable Diffusion)
- Midjourney API
- Azure OpenAI
- 其他自定义API

只需按照脚本中的`ImageGenerator`基类实现即可。

### Q: 生成的图片保存在哪里？

默认保存在 `/home/claude/images/` 目录，同时会复制到 `/mnt/user-data/outputs/` 供用户下载。

### Q: 可以批量生成图片吗？

可以！脚本支持在循环中调用：

```python
prompts = ["提示词1", "提示词2", "提示词3"]
for i, prompt in enumerate(prompts):
    subprocess.run([
        'python', 'scripts/generate_image.py',
        '--prompt', prompt,
        '--api', 'gemini',
        '--output', f'/home/claude/images/img_{i}.png'
    ])
```

## 最佳实践

1. **优先使用Gemini**
   - 性价比高
   - 速度快
   - 质量稳定

2. **重要封面用DALL-E HD**
   - 质量最高
   - 细节丰富
   - 适合重点文章

3. **测试环境用Claude原生**
   - 无需配置
   - 快速验证
   - 适合原型开发

4. **批量生成做好错误处理**
   ```python
   try:
       result = subprocess.run([...], check=True)
   except subprocess.CalledProcessError:
       print("生成失败，使用备选方案")
   ```

5. **缓存生成的图片**
   - 相同提示词不重复生成
   - 节省成本
   - 提高效率

## 安全提醒

⚠️ **不要将API密钥提交到版本控制**

在 `.gitignore` 中添加：
```
.env
*.key
secrets/
```

使用环境变量或配置文件管理API密钥。

## 技术支持

如遇到问题：
1. 查看脚本输出的错误信息
2. 检查API文档是否有更新
3. 验证API密钥是否有效
4. 确认API配额是否充足

---

配置完成后，skill就能自动调用生图API，为文章生成精美的配图了！🎨
