#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML转换工具 - 将爬取的JSON文章转换为美观的HTML文件

使用方法:
  python3 html_converter.py                        # 使用默认JSON文件
  python3 html_converter.py first_article_97855.json  # 指定JSON文件
  python3 html_converter.py first_article_97855.json -o my_article.html  # 指定输出文件
"""

import json
import re
import argparse
from datetime import datetime
from pathlib import Path

def clean_html_content(html_content):
    """清理HTML内容，移除不必要的属性，优化图片显示"""
    
    # 1. 移除 _src 属性（保留 src 属性）
    html_content = re.sub(r'\s+_src="[^"]*"', '', html_content)
    
    # 2. 修复img标签的样式属性
    # 添加style属性以支持CDN图片的加载
    html_content = re.sub(
        r'<img\s+([^>]*)src="([^"]*)"([^>]*)>',
        r'<img \1src="\2" loading="lazy"\3>',
        html_content
    )
    
    # 3. 移除多余的空格和标签
    html_content = re.sub(r'\s+', ' ', html_content)
    html_content = re.sub(r'>\s+<', '><', html_content)
    
    return html_content

def create_html_file(json_file, output_html=None):
    """从JSON文件读取内容，创建HTML文件"""
    
    # 确定输出文件名
    if output_html is None:
        json_path = Path(json_file)
        output_html = json_path.parent / f"{json_path.stem}.html"
    
    # 读取JSON文件
    print(f"📖 读取JSON文件: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get('src_title', '文章')
    content = data.get('src_content', '')
    read_count = data.get('read_count', 0)
    like_count = data.get('like_count', 0)
    author = data.get('src_user', '未知')
    create_time = data.get('create_time', '')
    src_url = data.get('src_url', '')
    
    print(f"✓ 读取成功")
    print(f"  标题: {title[:50]}")
    print(f"  内容长度: {len(content)} 字符")
    print(f"  图片数量: {content.count('<img')}")
    
    # 清理HTML内容
    print(f"🧹 清理HTML内容...")
    content = clean_html_content(content)
    
    # 创建完整的HTML文件
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            background-color: white;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            border-radius: 12px;
        }}
        
        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 25px;
            margin-bottom: 35px;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 20px;
            color: #1f2937;
            line-height: 1.4;
            word-wrap: break-word;
        }}
        
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 25px;
            color: #666;
            font-size: 14px;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .meta-item strong {{
            color: #2563eb;
            font-weight: 600;
        }}
        
        .meta-item span {{
            color: #666;
        }}
        
        .source-link {{
            color: #0ea5e9;
            text-decoration: none;
            font-size: 12px;
            transition: color 0.3s ease;
        }}
        
        .source-link:hover {{
            color: #2563eb;
            text-decoration: underline;
        }}
        
        .content {{
            font-size: 16px;
            line-height: 1.9;
            color: #444;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .content p {{
            margin-bottom: 18px;
            text-align: justify;
        }}
        
        .content h1 {{
            font-size: 26px;
            margin: 30px 0 20px 0;
            color: #1f2937;
        }}
        
        .content h2 {{
            font-size: 22px;
            margin: 28px 0 18px 0;
            color: #2563eb;
            border-left: 5px solid #2563eb;
            padding-left: 15px;
        }}
        
        .content h3 {{
            font-size: 18px;
            margin: 20px 0 15px 0;
            color: #1f2937;
        }}
        
        .content img {{
            max-width: 100%;
            height: auto;
            margin: 25px 0;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            display: block;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .content img:hover {{
            transform: scale(1.02);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
        }}
        
        .content span {{
            display: inline;
        }}
        
        .content b, .content strong {{
            color: #2563eb;
            font-weight: 600;
        }}
        
        .content u {{
            text-decoration: underline;
            text-decoration-style: wavy;
            text-decoration-color: #2563eb;
            text-underline-offset: 2px;
        }}
        
        .content i, .content em {{
            font-style: italic;
            color: #666;
        }}
        
        .content ul, .content ol {{
            margin: 15px 0 15px 30px;
        }}
        
        .content li {{
            margin-bottom: 8px;
        }}
        
        .content blockquote {{
            border-left: 4px solid #2563eb;
            padding-left: 15px;
            margin: 15px 0;
            color: #666;
            font-style: italic;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 25px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
        
        .footer p {{
            margin-bottom: 8px;
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                border-radius: 8px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .header {{
                padding-bottom: 18px;
                margin-bottom: 25px;
            }}
            
            .content {{
                font-size: 15px;
                line-height: 1.8;
            }}
            
            .content h2 {{
                font-size: 18px;
            }}
            
            .meta {{
                flex-direction: column;
                gap: 12px;
                font-size: 13px;
            }}
            
            .meta-item {{
                gap: 5px;
            }}
        }}
        
        @media (max-width: 480px) {{
            body {{
                padding: 10px;
            }}
            
            .container {{
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 18px;
            }}
            
            .content {{
                font-size: 14px;
            }}
        }}
        
        /* 打印样式 */
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                box-shadow: none;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="meta">
                <div class="meta-item">
                    <strong>👁️ 阅读：</strong>
                    <span>{read_count:,}</span>
                </div>
                <div class="meta-item">
                    <strong>👍 看好：</strong>
                    <span>{like_count}</span>
                </div>
                <div class="meta-item">
                    <strong>✍️ 作者：</strong>
                    <span>{author}</span>
                </div>
                <div class="meta-item">
                    <strong>📅 发布：</strong>
                    <span>{create_time.split(' ')[0] if create_time else '未知'}</span>
                </div>
                <div class="meta-item">
                    <strong>🔗 来源：</strong>
                    <a href="{src_url}" class="source-link" target="_blank">i云保社区</a>
                </div>
            </div>
        </div>
        
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>✨ 本页面由 i云保爬虫生成</p>
            <p>生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 图片加载错误处理
        document.querySelectorAll('img').forEach(img => {{
            img.onerror = function() {{
                this.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2220%22 fill=%22%23999%22 text-anchor=%22middle%22 dy=%22.3em%22%3E图片加载失败%3C/text%3E%3C/svg%3E';
                this.style.opacity = '0.6';
            }};
        }});
        
        // 为外部链接添加target="_blank"
        document.querySelectorAll('a').forEach(a => {{
            if (a.hostname !== window.location.hostname) {{
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
            }}
        }});
    </script>
</body>
</html>
"""
    
    # 写入HTML文件
    print(f"💾 生成HTML文件...")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✓ 完成！文件已保存: {output_html}")
    return output_html

def main():
    parser = argparse.ArgumentParser(
        description='将爬取的JSON文章转换为美观的HTML文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python3 html_converter.py                              # 使用first_article_97855.json
  python3 html_converter.py first_article_97867.json    # 转换指定JSON文件
  python3 html_converter.py first_article_97867.json -o my_article.html
        '''
    )
    
    parser.add_argument(
        'json_file',
        nargs='?',
        default='first_article_97855.json',
        help='JSON文件路径（默认: first_article_97855.json）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出HTML文件路径（默认: 与JSON文件同名）'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = create_html_file(args.json_file, args.output)
        print(f"\n🎉 转换成功！现在可以在浏览器中打开文件查看效果")
        print(f"📂 文件位置: {output_file}")
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {args.json_file}")
    except json.JSONDecodeError:
        print(f"❌ 错误: {args.json_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    main()

