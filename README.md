# i云保爬虫 (IyunbaoCrawler)

这是一个批量抓取i云保社区文章的爬虫工具。通过调用i云保官方API直接获取文章数据，具有高效、可靠的特点。

## ✨ 功能特性

- ✅ 批量抓取i云保文章（按postId从大到小遍历）
- ✅ 直接通过官方API获取数据，解析准确
- ✅ 提取文章标题、正文(HTML格式)、阅读数、看好数
- ✅ 自动保存第一篇文章到本地JSON文件用于验证
- ✅ 写入MySQL数据库
- ✅ 详细的日志记录和进度显示
- ✅ 请求延迟防止频率过高

## 🔧 环境要求

- Python 3.6+
- MySQL 5.7+
- 网络连接正常

## 📦 安装

1. 克隆或下载项目

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## ⚙️ 配置

编辑 `iyunbao_crawler.py` 中的数据库配置（已预配置）：

```python
DB_CONFIG = {
    'host': '172.105.225.120',
    'user': 'root',
    'password': 'lnmp.org#25295',
    'database': 'wordpress',
    'port': 3306
}
```

## 🚀 使用

### 方式1：命令行方式（推荐）

查看帮助信息：
```bash
python3 iyunbao_crawler.py --help
```

使用默认参数（从postId 97867开始，爬取3篇）：
```bash
python3 iyunbao_crawler.py
```

自定义参数（完整写法）：
```bash
python3 iyunbao_crawler.py --start 97867 --count 5
```

简写形式：
```bash
python3 iyunbao_crawler.py -s 97800 -c 10
```

### 方式2：Python代码方式

编辑 `example_custom_crawl.py` 并运行：

```python
from iyunbao_crawler import IyunbaoCrawler

crawler = IyunbaoCrawler()
crawler.crawl_articles(start_post_id=97867, count=10)
```

### 命令行参数说明

| 参数 | 简写 | 说明 | 默认值 | 例子 |
|-----|------|------|-------|------|
| `--start` | `-s` | 起始文章ID（postId） | 97867 | `--start 97800` |
| `--count` | `-c` | 要爬取的文章数量 | 3 | `--count 10` |

## 📊 数据映射

爬虫通过调用 `https://api.iyunbao.com/discover/open/v1/post/{postId}` API获取数据，并将其映射到数据库表如下：

| 爬取字段 | 数据库字段 | API字段 | 说明 |
|---------|-----------|--------|------|
| 文章URL | src_url | 构建 | 来源URL |
| 标题 | src_title | title | 文章标题 |
| 正文HTML | src_content | content | 文章内容（HTML格式） |
| 阅读数 | read_count | postPv | 页面访问次数 |
| 看好数 | like_count | likeNum | 点赞数 |
| 作者昵称 | src_user | author.nickname | 作者名称 |
| "iyunbao" | from_source | 固定值 | 来源标识 |

## 📝 输出

### 控制台输出
爬虫会实时输出爬取进度和日志，包括：
- 网络请求状态
- 数据解析结果
- 数据库操作状态
- 最终数据验证

### 本地文件
第一篇文章被保存为 `first_article_{postId}.json`，包含完整的文章数据：

```json
{
  "src_url": "https://bbs.iyunbao.com/m/community/topic?a=1&postId=97867",
  "src_title": "文章标题",
  "src_content": "<p>文章HTML内容</p>",
  "read_count": 12504,
  "like_count": 3,
  "src_user": "头条妹妹",
  "from_source": "iyunbao",
  "create_time": "2025-11-09 21:30:56.123096",
  "post_id": 97867
}
```

## 🔍 实现原理

1. **API发现**：通过Playwright追踪网络请求发现官方API
2. **数据获取**：调用 `https://api.iyunbao.com/discover/open/v1/post/{postId}` API
3. **数据解析**：从JSON响应中提取所需字段
4. **数据存储**：将数据保存到MySQL数据库
5. **验证输出**：保存第一篇文章到本地进行验证

## 📋 测试结果

✅ 成功爬取3篇文章：
1. 📄 **文章1**: 尊享e生·中高端2025版&PLUS（2025版）调整医疗机构清单
   - 阅读数: 12504
   - 看好数: 3

2. 📄 **文章2**: 星罗计划3.0来了‼️功能全面开放，等你来解锁！
   - 阅读数: 395
   - 看好数: 1

3. 📄 **文章3**: 蓝医保中端开单有礼
   - 阅读数: 1591
   - 看好数: 1

所有数据均已成功写入MySQL数据库。

## 🔧 排查问题

### 数据库连接失败
- 检查host、user、password是否正确
- 确保远程服务器允许该用户连接
- 检查防火墙设置
- 测试连接：`mysql -h 172.105.225.120 -u root -p`

### 网络请求失败
- 检查网络连接是否正常
- 确认API端点是否可访问：`curl https://api.iyunbao.com/discover/open/v1/post/97867`
- 检查是否被防火墙/代理阻止

### 找不到文章内容
- 部分文章可能被删除或URL已变更
- 检查postId是否有效
- 查看API返回的 `isSuccess` 字段

## 📄 许可证

MIT

## 👤 作者

Created with ❤️ for i云保数据爬取

---

**最后更新**：2025-11-09
