# 我的博客

个人博客站点，基于 Hugo + Congo 主题。

## 快速开始

### 首次使用

1. 安装 Hugo: https://gohugo.io/installation/
   - Mac: `brew install hugo`
   - Windows: `scoop install hugo-extended` 或下载安装包
   - Linux: `sudo apt install hugo` 或 `snap install hugo`

2. 克隆仓库（如果用这台新设备）:
   ```bash
   git clone https://github.com/lcy631zz/lcy631zz.github.io.git
   cd lcy631zz.github.io
   ```

3. 双击 `启动博客.bat`（Windows）或运行 `./start.sh`（Mac/Linux）

### 日常使用

1. 双击启动脚本
2. 浏览器打开 http://localhost:8082/admin 管理内容
3. 写完后点「一键发布」

### 手动命令

```bash
# 启动博客（端口 1313）
hugo server -p 1313

# 启动管理面板（端口 8082）
python3 admin-server.py
```

## 目录结构

- `content/blog/` — 博客文章
- `content/projects/` — 项目展示
- `data/zhai.json` — 摘抄数据
- `data/yin.json` — 照片数据
- `data/xing.json` — 旅行数据
- `layouts/` — 页面模板
- `assets/` — CSS 和 JS
