#!/bin/bash
# 新建项目（项目板块）
# 用法: ./new-project.sh "项目名称"

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}=== 新建项目 ===${NC}"

# 获取项目名称
if [ -z "$1" ]; then
    echo -e "${YELLOW}请输入项目名称:${NC}"
    read -r PROJECT_NAME
else
    PROJECT_NAME="$1"
fi

if [ -z "$PROJECT_NAME" ]; then
    echo -e "${RED}项目名称不能为空！${NC}"
    exit 1
fi

# 生成目录名（将空格转为中文空格或保留中文）
DIR="content/projects/$PROJECT_NAME"

# 检查是否已存在
if [ -d "$DIR" ]; then
    echo -e "${RED}错误：项目 '$PROJECT_NAME' 已经存在了！${NC}"
    exit 1
fi

# 创建目录
mkdir -p "$DIR"

# 获取今日日期
TODAY=$(date +"%Y-%m-%d")

# 获取项目描述
echo -e "${YELLOW}请输入项目简短描述:${NC}"
read -r PROJECT_DESC

# 获取标签
echo -e "${YELLOW}请输入标签（用空格分隔，例如: Python Web，直接回车跳过）:${NC}"
read -r TAGS_INPUT
TAGS="[]"
if [ -n "$TAGS_INPUT" ]; then
    TAGS=$(echo "$TAGS_INPUT" | tr ' ' '\n' | sed 's/^/"$/' | sed 's/$/"$/' | tr '\n' ',' | sed 's/,$//' | sed 's/^/[/' | sed 's/$/]/')
fi

# 获取项目链接
echo -e "${YELLOW}请输入项目链接（例如: https://github.com/lcy631zz/项目名，直接回车跳过）:${NC}"
read -r PROJECT_LINK

# 写入项目模板
cat > "$DIR/index.zh-Hans.md" << FILECONTENT
+++
title = "$PROJECT_NAME"
date = $TODAY
description = "$PROJECT_DESC"
image = "img/project-cover.jpg"
tags = $TAGS
link = "$PROJECT_LINK"
+++

## 项目简介

$PROJECT_DESC

### 项目描述

- 做了什么
- 用了什么技术
- 遇到了什么挑战
- 有什么收获

### 项目截图

把项目截图放到 \`static/img/\` 目录下，然后在这里引用：

![项目截图](/img/project-cover.jpg)

### 项目链接

- 📂 GitHub：[查看源码]($PROJECT_LINK)
FILECONTENT

echo -e "${GREEN}✓ 项目创建成功！${NC}"
echo ""
echo "文件位置: $DIR/index.zh-Hans.md"
echo ""
echo -e "${YELLOW}接下来你可以:${NC}"
echo "  1. 用任意编辑器打开上面的文件"
echo "  2. 补充项目描述、截图和链接"
echo "  3. 保存后运行 ${GREEN}hugo server${NC} 预览效果"
echo ""
echo -e "文件内容预览:"
echo "──────────────────────────────────────"
cat "$DIR/index.zh-Hans.md"
echo "──────────────────────────────────────"
