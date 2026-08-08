# 博客使用指南

## 一、首次在新电脑上设置（只需做一次）

### 你需要安装的 3 个软件：

| 软件 | 用途 | 下载地址 |
|------|------|----------|
| **Git** | 同步代码到 GitHub | https://git-scm.com/download/win |
| **Python 3** | 运行管理面板 | https://www.python.org/downloads/windows/ （安装时勾选 "Add Python to PATH"） |
| **Hugo Extended** | 本地预览网站 | https://github.com/gohugoio/hugo/releases （下载最新版的 Windows ZIP） |

### 安装步骤：

1. **Git**：下载安装，一路默认选项即可
2. **Python**：下载安装，**务必勾选 "Add Python to PATH"**，然后点 "Install Now"
3. **Hugo**：下载 ZIP → 解压到 `C:\hugo\` → 把 `C:\hugo` 加到系统 PATH 环境变量

### 验证安装：

打开 **PowerShell**（或 Git Bash），输入：

```bash
git --version
python3 --version
hugo version
```

三个都输出了版本号就说明安装成功。

### 获取博客代码：

```bash
git clone git@github.com:Eintv/my-website.git
cd my-website
```

> 如果提示 SSH 密钥错误，换成 HTTPS：
> ```bash
> git clone https://github.com/Eintv/my-website.git
> ```

---

## 二、日常使用（每次写博客时）

### 方式一：一键启动（推荐）

**Windows**：双击 `start.bat`

**WSL / Linux / macOS**：双击 `start.sh`，或在终端运行 `./start.sh`

启动后会看到两个地址：
- **Hugo 预览** → http://localhost:1313/ （浏览网站效果）
- **管理面板** → http://localhost:8082/admin （写文章、编辑内容）

### 方式二：分步启动

**终端 1**（预览网站）：
```bash
hugo server -D
```

**终端 2**（管理面板）：
```bash
python3 admin-server.py
```

---

## 三、发布到网站

1. 在管理面板里编辑/添加内容
2. 点 **"🚀 一键发布"**
3. 等 1-2 分钟，访问 https://eintv.github.io/my-website/ 查看

---

## 四、常见问题

**Q: 双击 start.bat 闪退？**
→ 说明 Python 或 Hugo 没装好，或者 PATH 没配对。打开 PowerShell 分别输入 `python3 --version` 和 `hugo version` 看看报什么错。

**Q: 端口被占用？**
→ 脚本会自动关闭占用端口的旧进程。如果还报错，重启电脑即可。

**Q: git push 失败？**
→ 确认已登录 GitHub。在 PowerShell 运行 `gh auth status` 检查。

**Q: 中文显示乱码？**
→ PowerShell 执行 `chcp 65001` 切换为 UTF-8。
