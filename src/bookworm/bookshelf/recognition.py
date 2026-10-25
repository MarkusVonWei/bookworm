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
import time
import logging
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

# 配置日志（由 config/logging.py 统一管理，此处仅获取 logger）
logger = logging.getLogger("bookworm.recognition")
logger.setLevel(logging.DEBUG)

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import MIMO_API_KEY, MIMO_API_BASE, LLM_MODEL

_DOUBAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


# ───────────────────────────────────────────
# Step 1: VLM 识别
# ───────────────────────────────────────────

async def recognize_book_from_image(image_path: str) -> Dict[str, Any]:
    """用 VL 大模型识别书籍封面, 提取标题 / 作者 / ISBN"""
    start_time = time.time()
    logger.info(f"[VLM] 开始识别: {image_path}")

    # 步骤0: 尝试条形码识别（快速，优先使用）
    barcode_result = _try_barcode_recognition(image_path)
    if barcode_result and barcode_result.get("isbn"):
        logger.info(f"[条形码] 识别到 ISBN: {barcode_result['isbn']}, 使用条形码结果")
        return {
            "title": None,
            "author": None,
            "isbn": barcode_result["isbn"],
            "publisher": None,
            "publish_date": None,
            "source": "barcode",
            "barcode_type": barcode_result.get("barcode_type"),
        }

    # 读取图片
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        logger.info(f"[VLM] 图片读取成功, base64长度: {len(image_data)}")
    except Exception as e:
        logger.error(f"[VLM] 图片读取失败: {e}")
        return {"error": f"图片读取失败: {str(e)}"}

    prompt = """请仔细识别这张书籍封面图片，提取以下信息并以JSON格式返回：

{
    "title": "书名（只返回中文书名，不要英文副标题）",
    "author": "作者",
    "isbn": "ISBN号（如果能在封面或条形码上看到，请仔细识别13位ISBN，以978或979开头）",
    "publisher": "出版社（如果能看到）",
    "publish_date": "出版日期（如果能看到）"
}

重要提示：
- 书名只返回中文主标题，不要包含英文翻译或副标题
- 例如：如果书名是"不原谅也没关系（Complex PTSD From Surviving to Thriving）"，只返回"不原谅也没关系"
- 请仔细查看封面底部或背面是否有条形码，条形码上方通常印有ISBN号
- ISBN通常是13位数字，以978或979开头，格式如 978-7-xxxx-xxxx-x
- 如果某个字段无法识别，请返回null
- 只返回JSON，不要其他内容"""

    logger.info(f"[VLM] 调用API: {MIMO_API_BASE}/chat/completions")
    logger.info(f"[VLM] 模型: {LLM_MODEL}")

    async with httpx.AsyncClient(timeout=15.0) as client:
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

            elapsed = time.time() - start_time
            logger.info(f"[VLM] API响应: status={response.status_code}, 耗时={elapsed:.2f}s")

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                finish_reason = result["choices"][0].get("finish_reason", "unknown")
                usage = result.get("usage", {})

                logger.info(f"[VLM] finish_reason: {finish_reason}")
                logger.info(f"[VLM] tokens: completion={usage.get('completion_tokens', 0)}, "
                          f"reasoning={usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)}")

                # 解析JSON
                original_content = content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                try:
                    parsed = json.loads(content.strip())
                    logger.info(f"[VLM] 解析成功: {json.dumps(parsed, ensure_ascii=False)}")

                    # 清洗 ISBN
                    if parsed.get("isbn"):
                        parsed["isbn"] = re.sub(r"[-\s]", "", parsed["isbn"])
                        logger.info(f"[VLM] ISBN清洗: {parsed['isbn']}")

                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"[VLM] JSON解析失败: {e}")
                    logger.error(f"[VLM] 原始内容: {original_content[:500]}")
                    return {"error": f"JSON解析失败: {str(e)}"}
            else:
                logger.error(f"[VLM] API调用失败: {response.status_code} - {response.text[:200]}")
                return {"error": f"API调用失败: {response.status_code}"}

        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            logger.error(f"[VLM] 请求超时: {elapsed:.2f}s")
            return {"error": "请求超时，请重试"}
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[VLM] 识别失败: {e}, 耗时={elapsed:.2f}s")
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
    start_time = time.time()
    logger.info(f"[豆瓣] suggest搜索: {title}")

    async with httpx.AsyncClient(timeout=5.0, headers=_DOUBAN_HEADERS) as client:
        try:
            response = await client.get(
                "https://book.douban.com/j/subject_suggest",
                params={"q": title}
            )

            elapsed = time.time() - start_time
            logger.info(f"[豆瓣] suggest响应: status={response.status_code}, 耗时={elapsed:.2f}s")

            if response.status_code != 200:
                logger.warning(f"[豆瓣] suggest请求失败: {response.status_code}")
                return None

            data = response.json()
            if not data:
                logger.info(f"[豆瓣] suggest无结果: {title}")
                return None

            # 取第一个结果
            item = data[0]
            result = {
                "title": item.get("title"),
                "author": item.get("author_name"),
                "cover_image": item.get("pic"),
                "publish_date": item.get("year"),
                "douban_id": item.get("id"),
                "douban_url": item.get("url"),
            }
            logger.info(f"[豆瓣] suggest找到: {result['title']} (id={result['douban_id']})")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"[豆瓣] suggest调用失败: {e}, 耗时={elapsed:.2f}s")
            return None




async def _fetch_from_douban_isbn(isbn: str) -> Optional[Dict[str, Any]]:
    """
    通过 ISBN 搜索豆瓣图书
    
    使用豆瓣 search API
    """
    start_time = time.time()
    logger.info(f"[豆瓣] ISBN搜索: {isbn}")
    
    async with httpx.AsyncClient(timeout=5.0, headers=_DOUBAN_HEADERS) as client:
        try:
            # 豆瓣搜索 API
            response = await client.get(
                "https://book.douban.com/j/subject_suggest",
                params={"q": isbn}
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[豆瓣] ISBN搜索响应: status={response.status_code}, 耗时={elapsed:.2f}s")
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data:
                logger.info(f"[豆瓣] ISBN搜索无结果: {isbn}")
                return None
            
            # 查找匹配的 ISBN
            for item in data:
                # 检查是否包含 ISBN
                if item.get("isbn") == isbn or isbn in str(item.get("title", "")):
                    result = {
                        "title": item.get("title"),
                        "author": item.get("author_name"),
                        "cover_image": item.get("pic"),
                        "publish_date": item.get("year"),
                        "douban_id": item.get("id"),
                        "douban_url": item.get("url"),
                        "isbn": isbn,
                    }
                    logger.info(f"[豆瓣] ISBN找到: {result['title']}")
                    return result
            
            # 如果没有精确匹配，返回第一个结果
            item = data[0]
            result = {
                "title": item.get("title"),
                "author": item.get("author_name"),
                "cover_image": item.get("pic"),
                "publish_date": item.get("year"),
                "douban_id": item.get("id"),
                "douban_url": item.get("url"),
                "isbn": isbn,
            }
            logger.info(f"[豆瓣] ISBN返回第一个结果: {result['title']}")
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"[豆瓣] ISBN搜索失败: {e}, 耗时={elapsed:.2f}s")
            return None

# ───────────────────────────────────────────
# Step 3: 豆瓣图书页面解析
# ───────────────────────────────────────────

async def _fetch_from_douban_page(douban_id: str) -> Optional[Dict[str, Any]]:
    """
    从豆瓣图书页面 HTML 解析 ISBN + 封面大图

    URL 格式: https://book.douban.com/subject/{id}/
    """
    start_time = time.time()
    logger.info(f"[豆瓣] 解析页面: https://book.douban.com/subject/{douban_id}/")

    async with httpx.AsyncClient(timeout=5.0, headers=_DOUBAN_HEADERS) as client:
        try:
            response = await client.get(
                f"https://book.douban.com/subject/{douban_id}/"
            )

            elapsed = time.time() - start_time
            logger.info(f"[豆瓣] 页面响应: status={response.status_code}, 耗时={elapsed:.2f}s")

            if response.status_code != 200:
                logger.warning(f"[豆瓣] 页面请求失败: {response.status_code}")
                return None

            html = response.text
            result = {}

            # 提取 ISBN (13位)
            isbn_match = re.search(r'"isbn"\s*:\s*"(\d{13})"', html)
            if not isbn_match:
                isbn_match = re.search(r'isbn13[^"]*"[^"]*"(\d{13})"', html)
            if isbn_match:
                result["isbn"] = isbn_match.group(1)
                logger.info(f"[豆瓣] 提取ISBN: {result['isbn']}")

            # 提取封面大图 (subject/l/ 目录下是大图)
            cover_match = re.search(
                r'"(https://img\d+\.doubanio\.com/view/subject/l/[^"]+)"', html
            )
            if cover_match:
                result["cover_image"] = cover_match.group(1)
                logger.info(f"[豆瓣] 提取封面: {result['cover_image'][:60]}...")

            # 提取出版社
            pub_match = re.search(r'"publisher"\s*:\s*"([^"]+)"', html)
            if pub_match:
                result["publisher"] = pub_match.group(1)
                logger.info(f"[豆瓣] 提取出版社: {result['publisher']}")

            if not result:
                logger.info(f"[豆瓣] 页面未提取到有用信息")
                return None

            logger.info(f"[豆瓣] 页面解析完成: {result}")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"[豆瓣] 页面解析失败: {e}, 耗时={elapsed:.2f}s")
            return None


# ───────────────────────────────────────────
# Step 4: Open Library (最终兜底)
# ───────────────────────────────────────────

async def _fetch_from_open_library(isbn: str = None, title: str = None) -> Optional[Dict[str, Any]]:
    """Open Library API 兜底"""
    start_time = time.time()
    logger.info(f"[OpenLibrary] 查询: isbn={isbn}, title={title}")

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

                elapsed = time.time() - start_time
                logger.info(f"[OpenLibrary] ISBN查询响应: status={response.status_code}, 耗时={elapsed:.2f}s")

                if response.status_code == 200:
                    data = response.json()
                    book_key = f"ISBN:{isbn}"
                    if book_key in data:
                        book = data[book_key]
                        result = {
                            "title": book.get("title"),
                            "author": ", ".join([a.get("name") for a in book.get("authors", [])]),
                            "publisher": ", ".join([p.get("name") for p in book.get("publishers", [])]),
                            "publish_date": book.get("publish_date"),
                            "isbn": isbn,
                            "cover_image": book.get("cover", {}).get("large"),
                            "description": book.get("notes") or book.get("description"),
                            "category": ", ".join([s.get("name") for s in book.get("subjects", [])[:3]])
                        }
                        logger.info(f"[OpenLibrary] ISBN找到: {result.get('title')}")
                        return result

            if title:
                response = await client.get(
                    "https://openlibrary.org/search.json",
                    params={"title": title, "limit": 1}
                )

                elapsed = time.time() - start_time
                logger.info(f"[OpenLibrary] 标题搜索响应: status={response.status_code}, 耗时={elapsed:.2f}s")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("docs") and len(data["docs"]) > 0:
                        book = data["docs"][0]
                        result = {
                            "title": book.get("title"),
                            "author": ", ".join(book.get("author_name", [])),
                            "publisher": ", ".join(book.get("publisher", [])[:1]),
                            "publish_date": book.get("first_publish_year"),
                            "isbn": next((i for i in book.get("isbn", []) if len(i) == 13), None),
                            "cover_image": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
                            "description": None,
                            "category": ", ".join(book.get("subject", [])[:3])
                        }
                        logger.info(f"[OpenLibrary] 标题找到: {result.get('title')}")
                        return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"[OpenLibrary] API调用失败: {e}, 耗时={elapsed:.2f}s")

    logger.info(f"[OpenLibrary] 未找到结果")
    return None


# ───────────────────────────────────────────
# 组合入口
# ───────────────────────────────────────────

async def fetch_book_metadata(isbn: str = None, title: str = None, author: str = None) -> Optional[Dict[str, Any]]:
    """
    获取书籍元数据

    优先级:
    1. ISBN 查询 (Open Library → 豆瓣 suggest)
    2. 标题搜索 (豆瓣 suggest → Open Library)
    """
    start_time = time.time()
    logger.info(f"[元数据] 开始查询: isbn={isbn}, title={title}, author={author}")

    # ── ISBN 查询 ──
    if isbn:
        logger.info(f"[元数据] 尝试ISBN查询: {isbn}")
        
        # 优先豆瓣 ISBN 搜索
        result = await _fetch_from_douban_isbn(isbn)
        if result:
            result["isbn"] = isbn
            elapsed = time.time() - start_time
            logger.info(f"[元数据] 豆瓣ISBN找到, 耗时={elapsed:.2f}s")
            return result

        # 备选: Open Library
        logger.info(f"[元数据] 豆瓣ISBN未找到, 尝试OpenLibrary")
        result = await _fetch_from_open_library(isbn=isbn)
        if result:
            result["isbn"] = isbn
            elapsed = time.time() - start_time
            logger.info(f"[元数据] OpenLibrary找到, 耗时={elapsed:.2f}s")
            return result

        # 最后尝试: 豆瓣 suggest
        logger.info(f"[元数据] OpenLibrary未找到, 尝试豆瓣suggest")
        result = await _fetch_from_douban_suggest(isbn)
        if result and result.get("douban_id"):
            logger.info(f"[元数据] 豆瓣suggest找到, 获取详细信息")
            page_data = await _fetch_from_douban_page(result["douban_id"])
            if page_data:
                result.update({k: v for k, v in page_data.items() if v})
            result["isbn"] = isbn
            elapsed = time.time() - start_time
            logger.info(f"[元数据] ISBN查询完成, 耗时={elapsed:.2f}s")
            return result

    # ── 标题搜索 ──
    if title:
        logger.info(f"[元数据] 尝试标题搜索: {title}")
        result = await _fetch_from_douban_suggest(title)
        if result and result.get("douban_id"):
            logger.info(f"[元数据] 豆瓣suggest找到, 获取详细信息")
            page_data = await _fetch_from_douban_page(result["douban_id"])
            if page_data:
                result.update({k: v for k, v in page_data.items() if v})
            elapsed = time.time() - start_time
            logger.info(f"[元数据] 标题搜索完成, 耗时={elapsed:.2f}s")
            return result

        logger.info(f"[元数据] 豆瓣suggest未找到, 尝试OpenLibrary")
        result = await _fetch_from_open_library(title=title)
        if result:
            elapsed = time.time() - start_time
            logger.info(f"[元数据] OpenLibrary找到, 耗时={elapsed:.2f}s")
            return result

    elapsed = time.time() - start_time
    logger.info(f"[元数据] 所有数据源均未找到, 耗时={elapsed:.2f}s")
    return None


async def search_books_external(keyword: str, limit: int = 10) -> list:
    """
    搜索外部书籍目录（豆瓣 suggest API）
    返回多条结果，用于"搜索添加"功能
    """
    import time
    start_time = time.time()
    logger.info(f"[外部搜索] keyword={keyword}")

    async with httpx.AsyncClient(timeout=5.0, headers=_DOUBAN_HEADERS) as client:
        try:
            response = await client.get(
                "https://book.douban.com/j/subject_suggest",
                params={"q": keyword}
            )
            elapsed = time.time() - start_time

            if response.status_code != 200:
                logger.warning(f"[外部搜索] 请求失败: {response.status_code}")
                return []

            data = response.json()
            if not data:
                logger.info(f"[外部搜索] 无结果: {keyword}")
                return []

            results = []
            for item in data[:limit]:
                results.append({
                    "title": item.get("title"),
                    "author": item.get("author_name"),
                    "cover_image": item.get("pic"),
                    "publish_date": item.get("year"),
                    "isbn": item.get("isbn13") or item.get("isbn10"),
                    "publisher": item.get("publisher"),
                    "douban_id": item.get("id"),
                    "douban_url": item.get("url"),
                })

            logger.info(f"[外部搜索] 找到 {len(results)} 条结果, 耗时 {elapsed:.2f}s")
            return results

        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"[外部搜索] 调用失败: {e}, 耗时 {elapsed:.2f}s")
            return []


def _try_barcode_recognition(image_path: str) -> Optional[Dict[str, Any]]:
    """尝试条形码识别"""
    try:
        from .barcode import recognize_barcode
        result = recognize_barcode(image_path)
        if result and result.get("isbn"):
            logger.info(f"[条形码] 识别成功: ISBN={result['isbn']}")
            return result
        elif result:
            logger.info(f"[条形码] 识别到条形码但无有效 ISBN: {result.get('barcode_data')}")
        return result
    except Exception as e:
        logger.debug(f"[条形码] 识别失败: {e}")
        return None
