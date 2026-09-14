"""书籍识别服务

识别流程:
1. MiMo VLM 识别封面 → 提取标题 / 作者 / ISBN
2. 豆瓣 suggest API → 按标题搜索，获取封面图 + subject_id
3. 豆瓣图书页面 HTML → 解析 ISBN + 封面大图 (兜底)
4. Open Library API → ISBN 查询 (最终兜底)

注意: 豆瓣图书 API (api.douban.com/v2) 已关闭, 使用的是 book.douban.com 的公开接口
"""

import base64
import json
import re
import sys
import logging
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import MIMO_API_KEY, MIMO_API_BASE, LLM_MODEL

logger = logging.getLogger("bookworm.recognition")

_DOUBAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


# ───────────────────────────────────────────
# Step 1: VLM 识别
# ───────────────────────────────────────────

async def recognize_book_from_image(image_path: str) -> Dict[str, Any]:
    """用 VL 大模型识别书籍封面, 提取标题 / 作者 / ISBN"""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    prompt = """请仔细识别这张书籍封面图片，提取以下信息并以JSON格式返回：

{
    "title": "书名",
    "author": "作者",
    "isbn": "ISBN号（如果能在封面或条形码上看到，请仔细识别13位ISBN，以978或979开头）",
    "publisher": "出版社（如果能看到）",
    "publish_date": "出版日期（如果能看到）"
}

重要提示：
- 请仔细查看封面底部或背面是否有条形码，条形码上方通常印有ISBN号
- ISBN通常是13位数字，以978或979开头，格式如 978-7-xxxx-xxxx-x
- 如果某个字段无法识别，请返回null
- 只返回JSON，不要其他内容"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{MIMO_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MIMO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "max_tokens": 4096
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                parsed = json.loads(content.strip())

                # 清洗 ISBN
                if parsed.get("isbn"):
                    parsed["isbn"] = re.sub(r"[-\s]", "", parsed["isbn"])

                return parsed
            else:
                logger.error(f"VLM API 调用失败: {response.status_code}")
                return {"error": f"API调用失败: {response.status_code}"}

        except Exception as e:
            logger.error(f"VLM 识别失败: {e}")
            return {"error": f"识别失败: {str(e)}"}


# ───────────────────────────────────────────
# Step 2: 豆瓣 suggest API
# ───────────────────────────────────────────

async def _fetch_from_douban_suggest(title: str) -> Optional[Dict[str, Any]]:
    """
    豆瓣图书 suggest API: book.douban.com/j/subject_suggest

    返回: title, url, pic (封面图), author_name, year, id
    无 API Key 需求, 免费公开接口
    """
    async with httpx.AsyncClient(timeout=10.0, headers=_DOUBAN_HEADERS) as client:
        try:
            response = await client.get(
                "https://book.douban.com/j/subject_suggest",
                params={"q": title}
            )

            if response.status_code != 200:
                return None

            data = response.json()
            if not data:
                return None

            # 取第一个结果
            item = data[0]
            return {
                "title": item.get("title"),
                "author": item.get("author_name"),
                "cover_image": item.get("pic"),
                "publish_date": item.get("year"),
                "douban_id": item.get("id"),
                "douban_url": item.get("url"),
            }

        except Exception as e:
            logger.warning(f"豆瓣 suggest API 调用失败: {e}")
            return None


# ───────────────────────────────────────────
# Step 3: 豆瓣图书页面解析
# ───────────────────────────────────────────

async def _fetch_from_douban_page(douban_id: str) -> Optional[Dict[str, Any]]:
    """
    从豆瓣图书页面 HTML 解析 ISBN + 封面大图

    URL 格式: https://book.douban.com/subject/{id}/
    """
    async with httpx.AsyncClient(timeout=10.0, headers=_DOUBAN_HEADERS) as client:
        try:
            response = await client.get(
                f"https://book.douban.com/subject/{douban_id}/"
            )

            if response.status_code != 200:
                return None

            html = response.text
            result = {}

            # 提取 ISBN (13位)
            isbn_match = re.search(r'"isbn"\s*:\s*"(\d{13})"', html)
            if not isbn_match:
                isbn_match = re.search(r'isbn13[^"]*"[^"]*"(\d{13})"', html)
            if isbn_match:
                result["isbn"] = isbn_match.group(1)

            # 提取封面大图 (subject/l/ 目录下是大图)
            cover_match = re.search(
                r'"(https://img\d+\.doubanio\.com/view/subject/l/[^"]+)"', html
            )
            if cover_match:
                result["cover_image"] = cover_match.group(1)

            # 提取出版社
            pub_match = re.search(r'"publisher"\s*:\s*"([^"]+)"', html)
            if pub_match:
                result["publisher"] = pub_match.group(1)

            return result if result else None

        except Exception as e:
            logger.warning(f"豆瓣图书页面解析失败: {e}")
            return None


# ───────────────────────────────────────────
# Step 4: Open Library (最终兜底)
# ───────────────────────────────────────────

async def _fetch_from_open_library(isbn: str = None, title: str = None) -> Optional[Dict[str, Any]]:
    """Open Library API 兜底"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if isbn:
                response = await client.get(
                    "https://openlibrary.org/api/books",
                    params={
                        "bibkeys": f"ISBN:{isbn}",
                        "format": "json",
                        "jscmd": "data"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    book_key = f"ISBN:{isbn}"
                    if book_key in data:
                        book = data[book_key]
                        return {
                            "title": book.get("title"),
                            "author": ", ".join([a.get("name") for a in book.get("authors", [])]),
                            "publisher": ", ".join([p.get("name") for p in book.get("publishers", [])]),
                            "publish_date": book.get("publish_date"),
                            "isbn": isbn,
                            "cover_image": book.get("cover", {}).get("large"),
                            "description": book.get("notes") or book.get("description"),
                            "category": ", ".join([s.get("name") for s in book.get("subjects", [])[:3]])
                        }

            if title:
                response = await client.get(
                    "https://openlibrary.org/search.json",
                    params={"title": title, "limit": 1}
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("docs") and len(data["docs"]) > 0:
                        book = data["docs"][0]
                        return {
                            "title": book.get("title"),
                            "author": ", ".join(book.get("author_name", [])),
                            "publisher": ", ".join(book.get("publisher", [])[:1]),
                            "publish_date": book.get("first_publish_year"),
                            "isbn": next((i for i in book.get("isbn", []) if len(i) == 13), None),
                            "cover_image": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
                            "description": None,
                            "category": ", ".join(book.get("subject", [])[:3])
                        }
        except Exception as e:
            logger.warning(f"Open Library API 调用失败: {e}")

    return None


# ───────────────────────────────────────────
# 组合入口
# ───────────────────────────────────────────

async def fetch_book_metadata(isbn: str = None, title: str = None, author: str = None) -> Optional[Dict[str, Any]]:
    """
    获取书籍元数据

    优先级:
    1. ISBN 查询 (豆瓣 suggest → 豆瓣页面 → Open Library)
    2. 标题搜索 (豆瓣 suggest → 豆瓣页面 → Open Library)
    """
    # ── ISBN 查询 ──
    if isbn:
        # 豆瓣 suggest 用 ISBN 搜索
        result = await _fetch_from_douban_suggest(isbn)
        if result and result.get("douban_id"):
            page_data = await _fetch_from_douban_page(result["douban_id"])
            if page_data:
                result.update({k: v for k, v in page_data.items() if v})
            result["isbn"] = isbn
            return result

        # Open Library 兜底
        result = await _fetch_from_open_library(isbn=isbn)
        if result:
            return result

    # ── 标题搜索 ──
    if title:
        # 豆瓣 suggest
        result = await _fetch_from_douban_suggest(title)
        if result and result.get("douban_id"):
            page_data = await _fetch_from_douban_page(result["douban_id"])
            if page_data:
                result.update({k: v for k, v in page_data.items() if v})
            return result

        # Open Library 兜底
        result = await _fetch_from_open_library(title=title)
        if result:
            return result

    return None
