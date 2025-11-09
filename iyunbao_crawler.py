#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import time
import logging
import argparse
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': '172.105.225.120',
    'user': 'root',
    'password': 'lnmp.org#25295',
    'database': 'wordpress',
    'port': 3306
}

# API基础配置
API_BASE_URL = 'https://api.iyunbao.com/discover/open/v1/post'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

class IyunbaoCrawler:
    def __init__(self):
        self.db_connection = None
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def clean_html_content(self, html_content):
        """清理HTML内容，移除不必要属性，确保图片能正常显示"""
        if not html_content:
            return html_content
        
        # 1. 移除 _src 属性（保留 src 属性）
        html_content = re.sub(r'\s+_src="[^"]*"', '', html_content)
        
        # 2. 移除其他可能导致问题的属性
        # 移除 style="" 中的空属性
        html_content = re.sub(r'\s+style=""', '', html_content)
        
        # 3. 清理多个空格
        html_content = re.sub(r'  +', ' ', html_content)
        
        # 4. 优化img标签 - 确保img标签格式正确
        # 移除img标签中的多余属性
        def fix_img_tag(match):
            img_tag = match.group(0)
            # 保留 src 属性，移除 _src
            img_tag = re.sub(r'\s+_src="[^"]*"', '', img_tag)
            return img_tag
        
        html_content = re.sub(r'<img[^>]*>', fix_img_tag, html_content)
        
        return html_content
        
    def connect_db(self):
        """连接数据库"""
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("✓ 数据库连接成功")
            return True
        except Error as e:
            logger.error(f"✗ 数据库连接失败: {e}")
            return False
    
    def close_db(self):
        """关闭数据库连接"""
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            logger.info("✓ 数据库连接已关闭")
    
    def fetch_article(self, post_id):
        """获取单篇文章（使用API）"""
        try:
            url = f"{API_BASE_URL}/{post_id}?_version=5.3.0&_client=2"
            logger.info(f"正在获取文章 #{post_id}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查是否成功
            if not data.get('isSuccess'):
                logger.warning(f"✗ 文章 #{post_id} 获取失败: {data.get('errorMsg')}")
                return None
            
            result = data.get('result', {})
            
            # 提取数据
            title = result.get('title', '无标题')
            content_html = result.get('content', '<p>无内容</p>')
            
            # 清理HTML内容 - 移除不必要的属性，确保图片能正常显示
            content_html = self.clean_html_content(content_html)
            
            read_count = int(result.get('postPv', -1))
            like_count = int(result.get('likeNum', -1))
            author_name = result.get('author', {}).get('nickname', '头条妹妹')
            
            article_data = {
                'src_url': f"https://bbs.iyunbao.com/m/community/topic?a=1&postId={post_id}",
                'src_title': title[:191],  # 限制长度
                'src_content': content_html,  # 已清理的HTML
                'read_count': read_count,
                'like_count': like_count,
                'src_user': author_name,
                'from_source': 'iyunbao',
                'create_time': datetime.now(),
                'post_id': post_id
            }
            
            logger.info(f"✓ 成功解析文章 #{post_id}")
            logger.info(f"  标题: {title[:80]}")
            logger.info(f"  阅读数: {read_count}, 看好数: {like_count}")
            
            return article_data
            
        except requests.RequestException as e:
            logger.error(f"✗ 网络请求失败 #{post_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"✗ 解析文章 #{post_id} 失败: {e}")
            return None
    
    def save_article_to_local(self, article_data):
        """保存第一篇文章到本地"""
        try:
            filename = f"first_article_{article_data['post_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"✓ 第一篇文章已保存到: {filename}")
            return True
        except Exception as e:
            logger.error(f"✗ 保存文章到本地失败: {e}")
            return False
    
    def check_article_exists(self, article_url):
        """检查文章URL是否已存在数据库中"""
        try:
            cursor = self.db_connection.cursor()
            query = "SELECT id FROM baoxianblog WHERE src_url = %s LIMIT 1"
            cursor.execute(query, (article_url,))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            logger.warning(f"⚠️  检查URL重复时出错: {e}")
            return False
    
    def insert_article_to_db(self, article_data):
        """将文章插入数据库"""
        try:
            cursor = self.db_connection.cursor()
            
            query = """
            INSERT INTO baoxianblog 
            (src_url, src_title, src_content, read_count, like_count, src_user, 
             from_source, create_time, update_time, isPublish, published_user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                article_data['src_url'],
                article_data['src_title'],
                article_data['src_content'],
                article_data['read_count'],
                article_data['like_count'],
                article_data['src_user'],
                article_data['from_source'],
                article_data['create_time'],
                article_data['create_time'],
                0,  # isPublish
                article_data['src_user']
            )
            
            cursor.execute(query, values)
            self.db_connection.commit()
            
            logger.info(f"✓ 文章已写入数据库: {article_data['src_title'][:60]}")
            cursor.close()
            return True
            
        except Error as e:
            logger.error(f"✗ 数据库写入失败: {e}")
            self.db_connection.rollback()
            return False
    
    def check_db_data(self):
        """查看数据库中已保存的文章"""
        try:
            cursor = self.db_connection.cursor()
            query = """
            SELECT id, src_title, read_count, like_count, src_user 
            FROM baoxianblog 
            WHERE from_source='iyunbao' 
            ORDER BY id DESC 
            LIMIT 5
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            logger.info("\n" + "=" * 80)
            logger.info("📊 数据库中的文章数据（最新5条）")
            logger.info("=" * 80)
            for row in results:
                logger.info(f"  ID: {row[0]:6} | 标题: {row[1][:50]:<50} | 阅读: {row[2]:<6} | 看好: {row[3]:<6} | 作者: {row[4]}")
            logger.info("=" * 80)
            
            cursor.close()
        except Error as e:
            logger.error(f"✗ 查询数据库失败: {e}")
    
    def crawl_articles(self, start_post_id=97867, count=3):
        """爬取指定数量的文章"""
        if not self.connect_db():
            logger.error("✗ 无法连接数据库，爬虫退出")
            return False
        
        try:
            current_post_id = start_post_id
            success_count = 0  # 新增文章数
            skip_count = 0     # 已存在（跳过）数
            fail_count = 0     # 真实失败数
            first_article_saved = False
            consecutive_fails = 0  # 连续失败次数
            max_consecutive_fails = 20  # 连续失败20次才停止
            
            while success_count < count and consecutive_fails < max_consecutive_fails:
                logger.info(f"\n{'='*80}")
                logger.info(f"📝 正在爬取第 {success_count + skip_count + 1}个 (postId: {current_post_id}, 成功: {success_count}/{count})")
                logger.info(f"{'='*80}")
                
                article_data = self.fetch_article(current_post_id)
                
                if article_data:
                    # 检查文章URL是否已存在
                    if self.check_article_exists(article_data['src_url']):
                        logger.info(f"⏭️  文章已存在数据库中（跳过）: {article_data['src_title'][:60]}")
                        skip_count += 1
                        consecutive_fails = 0  # 重置连续失败计数
                    else:
                        # 保存第一篇新文章到本地
                        if not first_article_saved:
                            self.save_article_to_local(article_data)
                            first_article_saved = True
                        
                        # 插入数据库
                        if self.insert_article_to_db(article_data):
                            success_count += 1
                            consecutive_fails = 0  # 重置连续失败计数
                            logger.info(f"✓ 成功爬取 {success_count}/{count} 篇文章 (新增, 已跳过 {skip_count} 篇)")
                        else:
                            logger.warning(f"✗ 插入数据库失败，跳过该文章")
                            fail_count += 1
                            consecutive_fails += 1
                else:
                    logger.warning(f"✗ 获取文章失败，跳过该文章")
                    fail_count += 1
                    consecutive_fails += 1
                
                # 处理下一篇文章（postId从大到小）
                current_post_id -= 1
                
                # 延迟请求，避免被反爬 (建议2-3秒)
                if success_count < count:
                    time.sleep(3)  # 增加到3秒以避免反爬
            
            # 显示最终统计
            logger.info(f"\n{'='*80}")
            logger.info(f"✓ 爬虫任务完成统计")
            logger.info(f"{'='*80}")
            logger.info(f"  新增文章: {success_count} 篇")
            logger.info(f"  已存在: {skip_count} 篇")
            logger.info(f"  失败: {fail_count} 篇")
            logger.info(f"  总处理: {success_count + skip_count + fail_count} 篇")
            
            if success_count >= count:
                logger.info(f"✓ 已成功爬取目标数量 {count} 篇文章")
            elif consecutive_fails >= max_consecutive_fails:
                logger.warning(f"⚠️  连续失败 {consecutive_fails} 次，停止爬虫")
            else:
                logger.warning(f"⚠️  仅成功爬取 {success_count}/{count} 篇新文章 (还跳过了 {skip_count} 篇已存在文章)")
            
            logger.info(f"{'='*80}\n")
            
            # 显示数据库中的数据
            self.check_db_data()
            
            return success_count >= count
            
        except Exception as e:
            logger.error(f"✗ 爬虫执行出错: {e}")
            return False
        finally:
            self.close_db()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='i云保爬虫 - 批量抓取i云保文章到数据库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例：
  python3 iyunbao_crawler.py                    # 使用默认参数（postId: 97867, 爬取3篇）
  python3 iyunbao_crawler.py --start 97867 --count 5   # 从97867开始，爬取5篇
  python3 iyunbao_crawler.py -s 97800 -c 10    # 简写形式
        '''
    )
    
    parser.add_argument(
        '--start', '-s',
        type=int,
        default=97867,
        help='起始文章ID（postId），默认：97867'
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=3,
        help='要爬取的文章数量，默认：3'
    )
    
    args = parser.parse_args()
    
    # 参数验证
    if args.start < 1:
        logger.error("✗ 起始ID必须大于0")
        return False
    
    if args.count < 1:
        logger.error("✗ 爬取数量必须大于0")
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("🚀 i云保爬虫启动")
    logger.info("=" * 80)
    logger.info(f"📝 参数配置：")
    logger.info(f"   起始ID (postId)：{args.start}")
    logger.info(f"   爬取数量：{args.count}")
    logger.info("=" * 80 + "\n")
    
    crawler = IyunbaoCrawler()
    
    # 根据参数爬取文章
    success = crawler.crawl_articles(start_post_id=args.start, count=args.count)
    
    if success:
        logger.info(f"\n✓ 任务完成！已成功爬取 {args.count} 篇文章并保存到数据库。")
    else:
        logger.error(f"\n✗ 任务未能全部完成（目标：{args.count}篇）。")
    
    return success


if __name__ == '__main__':
    main()
