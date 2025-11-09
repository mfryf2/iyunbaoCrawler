#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取纯净的HTML内容 - 直接从JSON或数据库获取，转换为可直接发布的HTML

使用方法:
  python3 extract_html.py first_article_97867.json
  或
  python3 extract_html.py --from-db  (从数据库获取最新文章)
"""

import json
import argparse
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': '172.105.225.120',
    'user': 'root',
    'password': 'lnmp.org#25295',
    'database': 'wordpress',
    'port': 3306
}

def extract_from_json(json_file):
    """从JSON文件提取HTML"""
    print(f"📖 读取JSON文件: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get('src_title', '文章')
    content = data.get('src_content', '')
    
    print(f"\n✓ 文章标题: {title}")
    print(f"✓ HTML长度: {len(content)} 字符")
    
    return title, content

def extract_from_db(post_id=None):
    """从数据库提取HTML"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if post_id:
            query = "SELECT src_title, src_content FROM baoxianblog WHERE id=%s LIMIT 1"
            cursor.execute(query, (post_id,))
        else:
            query = "SELECT src_title, src_content FROM baoxianblog WHERE from_source='iyunbao' ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            title, content = result
            print(f"✓ 从数据库获取成功")
            print(f"  标题: {title}")
            print(f"  HTML长度: {len(content)} 字符")
            return title, content
        else:
            print("✗ 未找到文章")
            return None, None
            
    except Error as e:
        print(f"✗ 数据库错误: {e}")
        return None, None

def process_html(html_content):
    """处理HTML，确保在博客中能正常显示"""
    
    # 1. 确保所有引号都是正常的双引号
    html_content = html_content.replace('\\"', '"')
    
    # 2. 移除任何可能存在的 _src 属性（再次确保）
    import re
    html_content = re.sub(r'\s+_src="[^"]*"', '', html_content)
    
    # 3. 确保img标签的完整性
    # 替换 <img src="..."> 为标准格式
    html_content = re.sub(r'<img\s+src="([^"]*)">', r'<img src="\1" alt="">', html_content)
    
    return html_content

def output_formats(title, html_content):
    """输出多种格式"""
    
    print("\n" + "="*80)
    print("📋 输出格式")
    print("="*80)
    
    # 格式1：纯HTML（可直接粘贴到博客）
    print("\n【格式1】纯HTML（直接粘贴到博客的HTML编辑器）")
    print("-" * 80)
    print(html_content)
    
    # 格式2：保存为HTML文件
    html_file = f"article_{title[:20]}.html"
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"\n【格式2】已保存为HTML文件: {html_file}")
    
    # 格式3：保存为纯HTML内容
    content_file = f"content_{title[:20]}.txt"
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"【格式3】已保存为纯文本: {content_file}")
    print(f"\n💡 提示: 直接从 {content_file} 复制内容粘贴到博客")
    
    # 输出到clipboard（如果支持）
    try:
        import subprocess
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(html_content.encode('utf-8'))
        print(f"\n✅ 已复制到剪贴板（Mac用户可直接Cmd+V粘贴到博客）")
    except:
        pass

def main():
    parser = argparse.ArgumentParser(
        description='提取纯净的HTML内容，用于博客发布',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python3 extract_html.py first_article_97867.json    # 从JSON提取
  python3 extract_html.py --from-db                   # 从数据库提取最新
  python3 extract_html.py --from-db --id 15791        # 从数据库提取指定ID
        '''
    )
    
    parser.add_argument(
        'json_file',
        nargs='?',
        help='JSON文件路径'
    )
    
    parser.add_argument(
        '--from-db',
        action='store_true',
        help='从数据库提取'
    )
    
    parser.add_argument(
        '--id',
        type=int,
        help='数据库文章ID'
    )
    
    args = parser.parse_args()
    
    if args.from_db:
        title, html_content = extract_from_db(args.id)
    elif args.json_file:
        title, html_content = extract_from_json(args.json_file)
    else:
        parser.print_help()
        return
    
    if not html_content:
        print("✗ 无法获取HTML内容")
        return
    
    # 处理HTML
    print("\n🧹 处理HTML...")
    html_content = process_html(html_content)
    
    # 输出
    output_formats(title, html_content)
    
    print("\n" + "="*80)
    print("✅ 完成！现在可以:")
    print("   1. 直接从剪贴板粘贴到博客（Cmd+V）")
    print("   2. 或打开保存的文件，复制内容到博客")
    print("="*80)

if __name__ == '__main__':
    main()

