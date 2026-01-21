# GitHub 推送指南

## 📋 当前状态

- ✅ Git 仓库已初始化
- ✅ 所有文件已提交 (commit: 37d7ea8)
- ✅ 分支已设置为 main
- ✅ 远程仓库已配置: https://github.com/solar-luna/Fully-automatic-article-generation-skill.git
- ⏳ 待完成: 推送到 GitHub

---

## 🚀 推送方法（3种选择）

### 方法1：使用 GitHub Personal Access Token (推荐)

**步骤：**

1. **创建 Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 设置名称：`ai-content-publisher`
   - 选择权限：勾选 `repo` (所有仓库权限)
   - 点击 "Generate token"
   - **立即复制** token（只显示一次！）

2. **配置 Git 用户信息**
   ```bash
   cd "/home/ubuntu/微信公众号和小红书自动化"

   # 设置你的 GitHub 用户名和邮箱
   git config --global user.name "solar-luna"
   git config --global user.email "your-email@example.com"  # 替换为你的邮箱
   ```

3. **推送到 GitHub**
   ```bash
   # 方式A: 在URL中包含token（一次性推送）
   git push -u https://YOUR_TOKEN@github.com/solar-luna/Fully-automatic-article-generation-skill.git main

   # 或

   # 方式B: Git会提示输入凭据
   git push -u origin main
   # Username: solar-luna
   # Password: [粘贴你的 token]
   ```

---

### 方法2：使用 SSH Key

**步骤：**

1. **生成 SSH Key**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   # 按 Enter 使用默认路径
   # 按 Enter 跳过密码（或设置密码）
   ```

2. **复制公钥**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. **添加到 GitHub**
   - 访问：https://github.com/settings/ssh/new
   - 标题：`ubuntu-server`
   - 粘贴公钥内容
   - 点击 "Add SSH key"

4. **更新远程仓库URL为SSH**
   ```bash
   cd "/home/ubuntu/微信公众号和小红书自动化"
   git remote set-url origin git@github.com:solar-luna/Fully-automatic-article-generation-skill.git
   ```

5. **推送**
   ```bash
   git push -u origin main
   ```

---

### 方法3：使用 GitHub CLI (gh)

**步骤：**

1. **安装 GitHub CLI**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **登录 GitHub**
   ```bash
   gh auth login
   # 选择: GitHub.com
   # 选择: HTTPS
   # 选择: Login with a web browser
   # 按提示在浏览器中完成认证
   ```

3. **推送**
   ```bash
   cd "/home/ubuntu/微信公众号和小红书自动化"
   git push -u origin main
   ```

---

## 🔧 快速推送脚本

**如果你已经有 Token，运行这个：**

```bash
#!/bin/bash
cd "/home/ubuntu/微信公众号和小红书自动化"

# 设置你的信息
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"  # 替换为你的 token
export GITHUB_USERNAME="solar-luna"
export GITHUB_EMAIL="your-email@example.com"  # 替换为你的邮箱

# 配置 Git
git config --global user.name "$GITHUB_USERNAME"
git config --global user.email "$GITHUB_EMAIL"

# 推送
git push -u https://${GITHUB_TOKEN}@github.com/solar-luna/Fully-automatic-article-generation-skill.git main

echo "✅ 推送成功！"
echo "🌐 访问: https://github.com/solar-luna/Fully-automatic-article-generation-skill"
```

保存为 `push.sh`，然后：
```bash
chmod +x push.sh
./push.sh
```

---

## ❓ 常见问题

### Q1: 推送时提示 "Authentication failed"
**A:** Token权限不足或已过期，重新生成token并确保勾选了 `repo` 权限。

### Q2: 推送时提示 "Permission denied"
**A:** SSH key未添加到GitHub，检查 https://github.com/settings/keys

### Q3: 仓库不存在
**A:** 需要先在GitHub创建仓库：
```bash
# 使用 gh CLI 创建仓库
gh repo create Fully-automatic-article-generation-skill --public --source=. --remote=origin --push
```

---

## ✅ 推送成功后

1. **访问仓库**
   https://github.com/solar-luna/Fully-automatic-article-generation-skill

2. **添加仓库描述**
   - 点击仓库页面右侧的 ⚙️ (Settings)
   - 添加描述：`🤖 AI内容自动发布系统 - 基于Claude的微信公众号和小红书全自动写作工具`
   - 添加标签：`ai`, `claude`, `wechat`, `xiaohongshu`, `automation`

3. **启用 GitHub Pages (可选)**
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main → /docs → Save

4. **创建第一个 Release**
   ```bash
   gh release create v1.0.0 --title "v1.0.0 - 首次发布" --notes "AI内容自动发布系统首次开源发布"
   ```

---

## 📞 需要帮助？

- GitHub文档: https://docs.github.com/cn
- Git文档: https://git-scm.com/doc

---

**当前项目统计：**
- 📁 86 个文件
- 📝 20,445 行代码
- 💾 72 MB
- 🌟 Ready to share!
