#!/bin/bash
# 新建旅行条目（行板块 - 旅游影像）
# 用法: ./new-travel.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

DATA_FILE="data/xing.json"

echo -e "${GREEN}=== 添加旅行影像 ===${NC}"
echo ""

# 检查数据文件是否存在
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}错误：找不到 $DATA_FILE${NC}"
    exit 1
fi

# 获取图片路径
echo -e "${YELLOW}请输入图片路径（例如: static/img/tokyo.jpg）:${NC}"
echo -e "${CYAN}提示: 先把图片放到 static/img/ 目录下${NC}"
read -r IMG_PATH

if [ -z "$IMG_PATH" ]; then
    echo -e "${RED}图片路径不能为空！${NC}"
    exit 1
fi

# 检查图片是否存在
if [ ! -f "$IMG_PATH" ]; then
    echo -e "${YELLOW}警告: 文件 '$IMG_PATH' 不存在，请确保图片已复制到该路径${NC}"
fi

# 获取地点
echo -e "${YELLOW}请输入地点（例如: 东京，直接回车跳过）:${NC}"
read -r PLACE

# 获取图片说明
echo -e "${YELLOW}请输入图片说明（直接回车跳过）:${NC}"
read -r CAPTION

# 使用 python3 安全地更新 JSON
python3 << PYEOF
import json
import sys

data_file = "$DATA_FILE"
img_path = "$IMG_PATH"
place = """$PLACE"""
caption = """$CAPTION"""

try:
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"\033[0;31m错误：无法读取 {data_file}: {e}\033[0m")
    sys.exit(1)

new_item = {"img": img_path}
if place:
    new_item["place"] = place
if caption:
    new_item["caption"] = caption

data["items"].append(new_item)

with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\033[0;32m✓ 旅行影像添加成功！\033[0m")
print(f"  图片: {img_path}")
if place:
    print(f"  地点: {place}")
if caption:
    print(f"  说明: {caption}")
print(f"\n  共 {len(data['items'])} 条影像")
PYEOF

echo ""
echo -e "${YELLOW}运行 ${GREEN}hugo server${NC} 预览效果${NC}"
