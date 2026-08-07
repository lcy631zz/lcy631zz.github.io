#!/bin/bash
# 新建博客文章
# 用法: ./new-post.sh "文章标题"

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 新建博客文章 ===${NC}"

# 获取标题
if [ -z "$1" ]; then
    echo -e "${YELLOW}请输入文章标题:${NC}"
    read -r TITLE
else
    TITLE="$1"
fi

if [ -z "$TITLE" ]; then
    echo -e "${RED}标题不能为空！${NC}"
    exit 1
fi

# 生成文件夹名（标题转为拼音或使用中文）
# 这里直接用标题作为文件夹名（支持中文）
DIR="content/blog/$TITLE"

# 检查是否已存在
if [ -d "$DIR" ]; then
    echo -e "${RED}错误：文章 '$TITLE' 已经存在了！${NC}"
    exit 1
fi

# 创建目录
mkdir -p "$DIR"

# 获取今日日期
TODAY=$(date +"%Y-%m-%d")

# 生成标签
echo -e "${YELLOW}请输入标签（用空格分隔，直接回车跳过）:${NC}"
read -r TAGS_INPUT
TAGS="[]"
if [ -n "$TAGS_INPUT" ]; then
    # 将空格分隔的标签转为 JSON 数组
    TAGS=$(echo "$TAGS_INPUT" | tr ' ' '\n' | sed 's/^/"$/' | sed 's/$/"$/' | tr '\n' ',' | sed 's/,$//' | sed 's/^/[/' | sed 's/$/]/')
fi

# 写入文章模板
cat > "$DIR/index.zh-Hans.md" << FILECONTENT
+++
title = "$TITLE"
date = $TODAY
description = ""
tags = $TAGS
+++

## 正文开始

在这里写下你的内容吧！

### 小标题

支持 Markdown 格式：
- **加粗**
- *斜体*
- [链接](https://example.com)

> 引用内容

\`\`\`python
# 代码块
print("Hello, World!")
\`\`\`
FILECONTENT

echo -e "${GREEN}✓ 文章创建成功！${NC}"
echo ""
echo "文件位置: $DIR/index.zh-Hans.md"
echo ""
echo -e "${YELLOW}接下来你可以:${NC}"
echo "  1. 用任意编辑器打开上面的文件"
echo "  2. 填写标题、描述和正文"
echo "  3. 保存后运行 ${GREEN}hugo server${NC} 预览效果"
echo ""
echo -e "文件内容预览:"
echo "──────────────────────────────────────"
cat "$DIR/index.zh-Hans.md"
echo "──────────────────────────────────────"
