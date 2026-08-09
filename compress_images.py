"""
图片压缩脚本 - 在 Windows 或 WSL 中运行
将 static/img/ 目录下的大图压缩到合理大小

用法：
  python3 compress_images.py              # 压缩所有图片到 1200px 宽, quality 75
  python3 compress_images.py --max-width 800 --quality 70   # 自定义参数
  python3 compress_images.py --dry-run   # 仅查看将要处理的信息，不实际修改

需要先安装 Pillow：
  pip install Pillow
"""
import os
import sys
import glob
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    print("错误：需要安装 Pillow")
    print("请先运行: pip install Pillow")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
SUPPORTED = ('.jpg', '.jpeg', '.png', '.webp')


def compress_image(path, max_width=1200, quality=75, dry_run=False):
    """Compress a single image, return (original_size, new_size, saved_bytes)"""
    original_size = os.path.getsize(path)
    ext = os.path.splitext(path)[1].lower()

    try:
        img = Image.open(path)

        # Convert RGBA to RGB for JPEG
        if ext in ('.jpg', '.jpeg') and img.mode in ('RGBA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if wider than max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        if dry_run:
            new_size_est = int(original_size * (0.3 if quality <= 75 else 0.5))
            return original_size, new_size_est, new_size_est - original_size

        # Save with compression
        temp_path = path + '.tmp'
        save_kwargs = {}
        if ext in ('.jpg', '.jpeg'):
            save_kwargs = {'quality': quality, 'optimize': True, 'progressive': True}
        elif ext == '.png':
            save_kwargs = {'optimize': True}
        elif ext == '.webp':
            save_kwargs = {'quality': quality, 'method': 6}

        img.save(temp_path, **save_kwargs)
        new_size = os.path.getsize(temp_path)

        if new_size < original_size:
            os.replace(temp_path, path)
            return original_size, new_size, original_size - new_size
        else:
            os.remove(temp_path)
            return original_size, new_size, 0

    except Exception as e:
        print(f"  跳过 {os.path.basename(path)}: {e}")
        return original_size, original_size, 0


def main():
    dry_run = '--dry-run' in sys.argv
    max_width = 1200
    quality = 75

    # Parse args
    if '--max-width' in sys.argv:
        idx = sys.argv.index('--max-width')
        if idx + 1 < len(sys.argv):
            max_width = int(sys.argv[idx + 1])

    if '--quality' in sys.argv:
        idx = sys.argv.index('--quality')
        if idx + 1 < len(sys.argv):
            quality = int(sys.argv[idx + 1])

    if not os.path.isdir(IMG_DIR):
        print(f"错误：图片目录不存在: {IMG_DIR}")
        sys.exit(1)

    files = []
    for ext in SUPPORTED:
        files.extend(glob.glob(os.path.join(IMG_DIR, f'*{ext}')))
    files.sort()

    if not files:
        print("未找到图片文件")
        sys.exit(0)

    print(f"{'[预览模式] ' if dry_run else ''}找到 {len(files)} 张图片")
    print(f"参数: max_width={max_width}, quality={quality}")
    print(f"目录: {IMG_DIR}")
    print()

    total_orig = 0
    total_new = 0
    compressed = 0

    for path in files:
        name = os.path.basename(path)
        orig, new, saved = compress_image(path, max_width, quality, dry_run)
        total_orig += orig
        total_new += new
        if saved > 0:
            compressed += 1
            status = f"-{saved/1024:.0f}KB ({new/1024:.0f}KB)" if not dry_run else f"~{saved/1024:.0f}KB 节省"
            print(f"  {name:<40} {orig/1024/1024:.1f}MB -> {status}")
        else:
            print(f"  {name:<40} {orig/1024/1024:.1f}MB (无需压缩或压缩后更大)")

    print()
    print(f"{'='*60}")
    print(f"总计: {len(files)} 张图片")
    print(f"原始总大小: {total_orig/1024/1024:.1f}MB")
    if not dry_run and compressed > 0:
        print(f"压缩后大小: {total_new/1024/1024:.1f}MB")
        print(f"节省:       {(total_orig-total_new)/1024/1024:.1f}MB ({(1-total_new/total_orig)*100:.0f}%)")
        print(f"处理图片数: {compressed}/{len(files)}")
    elif dry_run:
        print(f"预计压缩后: ~{int(total_orig*0.35/1024/1024)}MB (估计节省 ~65%)")

    if dry_run and compressed > 0:
        print()
        print("去掉 --dry-run 参数即可执行实际压缩")
    elif compressed == 0:
        print()
        print("所有图片都已经足够小，无需压缩")


if __name__ == '__main__':
    main()
