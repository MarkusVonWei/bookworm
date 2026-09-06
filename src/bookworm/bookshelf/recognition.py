"""书籍识别服务"""

import base64
import json
import sys
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

# 以项目根目录为基准，确保能导入 config 模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import MIMO_API_KEY, MIMO_API_BASE, LLM_MODEL


async def recognize_book_from_image(image_path: str) -> Dict[str, Any]:
    """
    从图片识别书籍信息
    
    使用VL大模型（MiMo 2.5）识别书籍封面，提取书籍metadata
    """
    # 读取图片并转为base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # 构建提示词
    prompt = """请识别这张书籍封面图片，提取以下信息并以JSON格式返回：
{
    "title": "书名",
    "author": "作者",
    "publisher": "出版社",
    "publish_date": "出版日期",
    "isbn": "ISBN号（如果能看到）",
    "category": "分类/类型"
}

如果某个字段无法识别，请返回null。只返回JSON，不要其他内容。"""
    
    # 调用MiMo VL API
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
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
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
                
                # 解析JSON
                # 尝试提取JSON部分
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                return json.loads(content.strip())
            else:
                return {"error": f"API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"识别失败: {str(e)}"}


async def fetch_book_metadata(isbn: str = None, title: str = None, author: str = None) -> Optional[Dict[str, Any]]:
    """
    获取书籍元数据
    
    优先使用ISBN查询，其次使用书名和作者组合查询
    数据源：豆瓣图书API + Open Library API
    """
    metadata = None
    
    # 1. 如果有ISBN，先尝试Open Library
    if isbn:
        metadata = await _fetch_from_open_library(isbn=isbn)
        if metadata:
            return metadata
    
    # 2. 尝试豆瓣图书API
    if title:
        metadata = await _fetch_from_douban(title, author)
        if metadata:
            return metadata
    
    # 3. 最后尝试Open Library搜索
    if title:
        metadata = await _fetch_from_open_library(title=title)
        if metadata:
            return metadata
    
    return None


async def _fetch_from_douban(title: str, author: str = None) -> Optional[Dict[str, Any]]:
    """从豆瓣图书API获取数据"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            query = title
            if author:
                query = f"{title} {author}"
            
            response = await client.get(
                "https://api.douban.com/v2/book/search",
                params={
                    "q": query,
                    "count": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("books") and len(data["books"]) > 0:
                    book = data["books"][0]
                    return {
                        "title": book.get("title"),
                        "author": ", ".join(book.get("author", [])),
                        "publisher": book.get("publisher"),
                        "publish_date": book.get("pubdate"),
                        "isbn": book.get("isbn13") or book.get("isbn10"),
                        "cover_image": book.get("image"),
                        "description": book.get("summary"),
                        "category": ", ".join(book.get("category", []))
                    }
        except Exception as e:
            print(f"豆瓣API调用失败: {e}")
    
    return None


async def _fetch_from_open_library(isbn: str = None, title: str = None) -> Optional[Dict[str, Any]]:
    """从Open Library API获取数据"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if isbn:
                # ISBN查询
                response = await client.get(
                    f"https://openlibrary.org/api/books",
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
                # 标题搜索
                response = await client.get(
                    "https://openlibrary.org/search.json",
                    params={
                        "title": title,
                        "limit": 1
                    }
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
                            "isbn": next((isbn for isbn in book.get("isbn", []) if len(isbn) == 13), None),
                            "cover_image": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
                            "description": None,
                            "category": ", ".join(book.get("subject", [])[:3])
                        }
        except Exception as e:
            print(f"Open Library API调用失败: {e}")
    
    return None
