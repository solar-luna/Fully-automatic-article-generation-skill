# Windows 系统使用指南

本文档专门为 Windows 用户提供详细的安装和使用说明。

## 📋 前置要求

### 1. 安装 Python

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.10 或更高版本
3. **重要**：安装时勾选 "Add Python to PATH"
4. 验证安装：

```cmd
python --version
pip --version
```

### 2. 安装 Git（可选，用于克隆仓库）

1. 访问 https://git-scm.com/download/win
2. 下载并安装 Git for Windows
3. 使用默认设置即可

### 3. 获取 Claude Code 账号

访问 https://claude.ai/claude-code 注册或登录

## 🚀 安装步骤

### 方法 1：使用 Git 克隆（推荐）

```cmd
# 打开 PowerShell 或 CMD
cd %USERPROFILE%\Documents

# 克隆仓库
git clone https://github.com/your-username/ai-content-publisher.git

# 进入目录
cd ai-content-publisher
```

### 方法 2：手动下载

1. 访问 GitHub 仓库页面
2. 点击绿色的 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压到 `C:\Users\YourName\Documents\ai-content-publisher`

## ⚙️ 配置环境

### 1. 安装 Python 依赖

```cmd
# 在项目目录中打开 PowerShell 或 CMD

# 安装依赖
pip install anthropic requests pyyaml feedparser beautifulsoup4 lxml

# 验证安装
python -c "import anthropic; print('OK')"
```

### 2. 创建配置文件

由于 Windows 不支持 `.sh` 脚本，我们需要创建 `.bat` 配置文件：

**创建 `config\config.bat`**：

```batch
@echo off
REM AI 内容发布系统配置文件

REM ==================== Claude API 配置 ====================
set ANTHROPIC_API_KEY=your-anthropic-api-key-here
set ANTHROPIC_BASE_URL=https://api.anthropic.com

REM ==================== 微信公众号配置 ====================
set WECHAT_APPID=your-wechat-appid-here
set WECHAT_SECRET=your-wechat-secret-here

REM ==================== 小红书配置 ====================
set XHS_API_URL=http://localhost:18060
set XHS_IMAGE_DIR=C:\path\to\xiaohongshu-mcp\docker\images

REM ==================== 其他配置 ====================
set ARTICLE_AUTHOR=你的公众号名称
set OUTPUT_DIR=%USERPROFILE%\Documents\生成记录
set LOG_FILE=%USERPROFILE%\Documents\ai-content.log
```

### 3. 创建启动脚本

**创建 `run.bat`** 在项目根目录：

```batch
@echo off
echo ========================================
echo AI 内容自动发布系统
echo ========================================
echo.

REM 加载配置
call config\config.bat

REM 检查 API Key
if "%ANTHROPIC_API_KEY%"=="your-anthropic-api-key-here" (
    echo [错误] 请先配置 API Key
    echo 编辑 config\config.bat 文件并填入你的密钥
    pause
    exit /b 1
)

echo [信息] 配置已加载
echo [信息] 开始生成文章...
echo.

REM 执行 Python 脚本
python skills\wechat-tech-writer\generate.py ^
    --topic "AI技术前沿：%date%" ^
    --url "https://www.example.com" ^
    --type "new_tool" ^
    --output "%OUTPUT_DIR%\%date:~0,10%" ^
    --mode standard

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [成功] 文章生成完成！
    echo ========================================
    echo 输出目录: %OUTPUT_DIR%\%date:~0,10%
) else (
    echo.
    echo ========================================
    echo [失败] 文章生成失败
    echo ========================================
)

echo.
pause
```

## 📝 使用方法

### 方法 1：双击运行

1. 找到 `run.bat` 文件
2. 双击运行
3. 等待脚本完成
4. 查看生成的文章

### 方法 2：命令行运行

```cmd
# 打开 PowerShell/CMD，进入项目目录
cd C:\Users\YourName\Documents\ai-content-publisher

# 运行脚本
run.bat
```

### 方法 3：手动运行 Python 脚本

```cmd
# 加载配置
call config\config.bat

# 运行文章生成
python skills\wechat-tech-writer\generate.py ^
    --topic "测试文章" ^
    --url "https://example.com" ^
    --type "new_tool" ^
    --output "%USERPROFILE%\Documents\test_article" ^
    --mode standard

# 查看结果
dir %USERPROFILE%\Documents\test_article
type %USERPROFILE%\Documents\test_article\article.md
```

## ⏰ 设置定时任务

### 使用 Windows 任务计划程序

#### 1. 打开任务计划程序

- 按 `Win + R`
- 输入 `taskschd.msc`
- 回车

#### 2. 创建基本任务

1. 点击右侧 "创建基本任务"
2. 名称：`AI内容自动发布`
3. 描述：`每天自动生成并发布 AI 文章`
4. 点击 "下一步"

#### 3. 设置触发器

1. 选择 "每天"
2. 开始时间：例如 `08:00:00`
3. 重复间隔：`1天`
4. 点击 "下一步"

#### 4. 设置操作

1. 选择 "启动程序"
2. 程序或脚本：
   ```
   C:\Users\YourName\Documents\ai-content-publisher\run.bat
   ```
3. 起始于：
   ```
   C:\Users\YourName\Documents\ai-content-publisher
   ```
4. 点击 "下一步"

#### 5. 完成设置

1. 勾选 "当单击'完成'时，打开此任务属性的对话框"
2. 点击 "完成"

#### 6. 高级设置（可选）

在属性对话框中：

- **常规**标签：
  - 勾选 "不管用户是否登录都要运行"
  - 勾选 "使用最高权限运行"

- **触发器**标签：
  - 点击 "新建" 添加更多时间（如 12:00、18:00）

- **条件**标签：
  - 取消勾选 "只有在计算机使用交流电源时才启动此任务"

- **设置**标签：
  - 勾选 "如果任务失败，按以下方式重新启动"
  - 勾选 "如果请求后任务还在运行，强行将其停止"

### 使用 PowerShell 创建任务（进阶）

```powershell
# 以管理员身份运行 PowerShell

# 创建任务触发器（每天 8:00、12:00、18:00）
$trigger1 = New-ScheduledTaskTrigger -Daily -At 8:00AM
$trigger2 = New-ScheduledTaskTrigger -Daily -At 12:00PM
$trigger3 = New-ScheduledTaskTrigger -Daily -At 6:00PM

# 创建任务操作
$action = New-ScheduledTaskAction -Execute "C:\Users\YourName\Documents\ai-content-publisher\run.bat" -WorkingDirectory "C:\Users\YourName\Documents\ai-content-publisher"

# 创建任务主体
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U -RunLevel Highest

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
Register-ScheduledTask -TaskName "AI内容自动发布" -Trigger $trigger1,$trigger2,$trigger3 -Action $action -Principal $principal -Settings $settings
```

## 🐛 Windows 特有问题

### 问题 1：中文路径乱码

**解决方案**：

1. 设置 UTF-8 编码：
```cmd
chcp 65001
```

2. 在 `run.bat` 开头添加：
```batch
@echo off
chcp 65001 >nul
```

### 问题 2：权限不足

**解决方案**：

1. 右键点击 `run.bat`
2. 选择 "以管理员身份运行"

或在 PowerShell 中：
```powershell
Start-Process run.bat -Verb RunAs
```

### 问题 3：Python 找不到

**解决方案**：

1. 检查 Python 是否在 PATH 中：
```cmd
where python
```

2. 如果找不到，手动添加 Python 路径：
```batch
set PATH=%PATH%;C:\Python310;C:\Python310\Scripts
```

### 问题 4：定时任务不运行

**排查步骤**：

1. 检查任务历史记录：
   - 任务计划程序 → 查看 → 显示所有正在运行的任务

2. 查看日志文件：
```cmd
type %USERPROFILE%\Documents\ai-content.log
```

3. 手动运行测试：
   - 右键点击任务
   - 选择 "运行"

## 💡 Windows 使用技巧

### 1. 创建桌面快捷方式

1. 右键点击 `run.bat`
2. 选择 "发送到" → "桌面快捷方式"
3. 可选：更改图标
   - 右键快捷方式 → 属性 → 更改图标

### 2. 后台运行（隐藏窗口）

创建 `run_silent.vbs`：

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\Users\YourName\Documents\ai-content-publisher\run.bat" & Chr(34), 0
Set WshShell = Nothing
```

双击 `run_silent.vbs` 即可无窗口运行。

### 3. 查看实时日志

使用 PowerShell：

```powershell
Get-Content $env:USERPROFILE\Documents\ai-content.log -Wait -Tail 50
```

或使用 `tail` for Windows：https://github.com/LukeLR/tail-for-windows

## 📞 获取帮助

如果遇到 Windows 特有问题：

1. 查看 [安装教程](INSTALL.md)
2. 查看 [常见问题](../README.md#常见问题)
3. 提交 Issue 并注明是 Windows 系统

## 🎉 开始使用

配置完成后，你可以：

- 双击 `run.bat` 手动生成文章
- 设置定时任务自动运行
- 查看生成的文章在 `文档\生成记录` 目录

---

📚 返回 [主文档](../README.md) | [安装教程](INSTALL.md)
