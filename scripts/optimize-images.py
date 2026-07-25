#!/usr/bin/env python3
"""批量优化图片：PNG转WebP，JPG压缩"""

import os
import sys
from PIL import Image
from pathlib import Path

IMAGES_DIR = Path(r'c:\Users\cn\.trae-cn\work\6a16a760ff8af3f6424fba73\异宠网站\yichong-site\public\images')

# 目标：hero/封面图 < 150KB，其他 < 100KB
# 策略：
# - PNG -> WebP (质量85)
# - JPG -> 压缩JPG (质量80) 或 WebP (质量85)

def optimize_image(filepath):
    """优化单张图片，返回新文件路径和节省的体积"""
    original_size = filepath.stat().st_size
    ext = filepath.suffix.lower()
    
    img = Image.open(filepath)
    
    # 转换为RGB（去除alpha通道，减少体积）
    if img.mode in ('RGBA', 'P'):
        # 对于有透明通道的，保留WebP的alpha支持
        if ext == '.png':
            # PNG转WebP，保留透明度
            new_path = filepath.with_suffix('.webp')
            img.save(new_path, 'WEBP', quality=85, method=6)
        else:
            # 其他格式转RGB
            img = img.convert('RGB')
            new_path = filepath.with_suffix('.webp')
            img.save(new_path, 'WEBP', quality=85, method=6)
    else:
        # 无透明通道，直接转WebP
        new_path = filepath.with_suffix('.webp')
        img.save(new_path, 'WEBP', quality=85, method=6)
    
    new_size = new_path.stat().st_size
    saved = original_size - new_size
    saved_pct = (saved / original_size * 100) if original_size > 0 else 0
    
    # 如果WebP反而更大（极少数情况），保留原格式但压缩
    if new_size > original_size * 0.9 and ext == '.jpg':
        new_path.unlink()
        new_path = filepath
        img.save(filepath, 'JPEG', quality=80, optimize=True)
        new_size = filepath.stat().st_size
        saved = original_size - new_size
        saved_pct = (saved / original_size * 100) if original_size > 0 else 0
    
    return new_path, original_size, new_size, saved, saved_pct

def main():
    total_original = 0
    total_new = 0
    converted = []
    
    # 处理所有图片
    for filepath in sorted(IMAGES_DIR.iterdir()):
        if filepath.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            continue
        
        # 跳过已经优化过的WebP（除非它很大）
        if filepath.suffix.lower() == '.webp' and filepath.stat().st_size < 150000:
            continue
        
        try:
            new_path, orig, new, saved, pct = optimize_image(filepath)
            total_original += orig
            total_new += new
            
            action = "转换" if new_path.suffix != filepath.suffix else "压缩"
            print(f"{action}: {filepath.name:35s} {orig/1024:7.1f}KB -> {new/1024:7.1f}KB  节省 {pct:5.1f}%")
            
            if new_path != filepath:
                converted.append((filepath.name, new_path.name))
                # 删除原文件
                filepath.unlink()
            
        except Exception as e:
            print(f"错误: {filepath.name} - {e}")
    
    print(f"\n{'='*60}")
    print(f"总计: {total_original/1024/1024:.2f}MB -> {total_new/1024/1024:.2f}MB")
    print(f"节省: {(total_original-total_new)/1024/1024:.2f}MB ({(total_original-total_new)/total_original*100:.1f}%)")
    print(f"转换文件数: {len(converted)}")

if __name__ == '__main__':
    main()
