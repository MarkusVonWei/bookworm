"""书架API接口"""

import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from ..database import get_db
from .models import Book, ReadingRecord, ReadingStatus
from .service import BookshelfService
from .recognition import recognize_book_from_image, fetch_book_metadata

router = APIRouter(prefix="/api/bookshelf", tags=["书架"])

# 上传目录
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ========== 请求/响应模型 ==========

class BookCreate(BaseModel):
    """添加书籍请求"""
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    user_status: str = "想读"


class BookUpdate(BaseModel):
    """更新书籍请求"""
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    user_status: Optional[str] = None
    user_rating: Optional[float] = None


class ReadingRecordCreate(BaseModel):
    """添加阅读记录请求"""
    content: Optional[str] = None
    excerpt: Optional[str] = None
    page_number: Optional[int] = None
    tags: Optional[str] = None


class BookResponse(BaseModel):
    """书籍响应"""
    id: int
    title: str
    author: Optional[str]
    publisher: Optional[str]
    publish_date: Optional[str]
    isbn: Optional[str]
    cover_image: Optional[str]
    description: Optional[str]
    category: Optional[str]
    user_status: str
    user_rating: Optional[float]
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime]
    records_count: int = 0

    class Config:
        from_attributes = True


class ReadingRecordResponse(BaseModel):
    """阅读记录响应"""
    id: int
    book_id: int
    content: Optional[str]
    excerpt: Optional[str]
    page_number: Optional[int]
    tags: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    """统计信息响应"""
    total_books: int
    want_to_read: int
    reading: int
    finished: int
    total_records: int
    shelf_age_days: int


# ========== API接口 ==========

@router.get("/books", response_model=List[BookResponse])
def get_books(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取所有书籍"""
    service = BookshelfService(db)
    
    if status:
        try:
            reading_status = ReadingStatus(status)
            books = service.get_books_by_status(reading_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    else:
        books = service.get_all_books()
    
    # 添加记录数量
    result = []
    for book in books:
        records_count = len(service.get_reading_records(book.id))
        book_dict = BookResponse.model_validate(book)
        book_dict.records_count = records_count
        result.append(book_dict)
    
    return result


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """获取单本书籍"""
    service = BookshelfService(db)
    book = service.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    records_count = len(service.get_reading_records(book.id))
    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = records_count
    
    return book_dict


@router.post("/books", response_model=BookResponse)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """添加书籍"""
    service = BookshelfService(db)
    
    # 转换状态
    try:
        status = ReadingStatus(book_data.user_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    book_dict = book_data.model_dump()
    book_dict["user_status"] = status
    
    book = service.add_book(book_dict)
    
    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = 0
    
    return book_dict


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db)
):
    """更新书籍"""
    service = BookshelfService(db)
    
    book_dict = book_data.model_dump(exclude_unset=True)
    
    # 转换状态
    if "user_status" in book_dict:
        try:
            book_dict["user_status"] = ReadingStatus(book_dict["user_status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    
    book = service.update_book(book_id, book_dict)
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    records_count = len(service.get_reading_records(book.id))
    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = records_count
    
    return book_dict


@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """删除书籍"""
    service = BookshelfService(db)
    
    if not service.delete_book(book_id):
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    return {"message": "删除成功"}


@router.put("/books/{book_id}/status")
def update_reading_status(
    book_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """更新阅读状态"""
    service = BookshelfService(db)
    
    try:
        reading_status = ReadingStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    book = service.update_reading_status(book_id, reading_status)
    
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    return {"message": "状态更新成功", "status": status}


@router.get("/books/{book_id}/records", response_model=List[ReadingRecordResponse])
def get_reading_records(book_id: int, db: Session = Depends(get_db)):
    """获取书籍的阅读记录"""
    service = BookshelfService(db)
    
    # 检查书籍是否存在
    book = service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    records = service.get_reading_records(book_id)
    return records


@router.post("/books/{book_id}/records", response_model=ReadingRecordResponse)
def create_reading_record(
    book_id: int,
    record_data: ReadingRecordCreate,
    db: Session = Depends(get_db)
):
    """添加阅读记录"""
    service = BookshelfService(db)
    
    record = service.add_reading_record(book_id, record_data.model_dump())
    
    if not record:
        raise HTTPException(status_code=404, detail="书籍不存在")
    
    return record


@router.get("/records", response_model=List[ReadingRecordResponse])
def get_all_records(db: Session = Depends(get_db)):
    """获取所有阅读记录"""
    service = BookshelfService(db)
    return service.get_all_records()


@router.get("/search", response_model=List[BookResponse])
def search_books(keyword: str, db: Session = Depends(get_db)):
    """搜索书籍"""
    service = BookshelfService(db)
    books = service.search_books(keyword)
    
    result = []
    for book in books:
        records_count = len(service.get_reading_records(book.id))
        book_dict = BookResponse.model_validate(book)
        book_dict.records_count = records_count
        result.append(book_dict)
    
    return result


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """获取统计信息"""
    service = BookshelfService(db)
    return service.get_statistics()


# ========== 书籍识别 ==========

class RecognizeResponse(BaseModel):
    """识别结果响应"""
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: str  # 上传的图片URL


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_book(file: UploadFile = File(...)):
    """
    识别书籍
    
    上传书籍封面图片，使用VL大模型识别书籍信息
    """
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    # 保存上传的文件
    file_ext = Path(file.filename).suffix or ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 识别书籍
    recognition_result = await recognize_book_from_image(str(file_path))
    
    if "error" in recognition_result:
        raise HTTPException(status_code=500, detail=recognition_result["error"])
    
    # 尝试获取更详细的元数据
    metadata = None
    if recognition_result.get("isbn"):
        metadata = await fetch_book_metadata(isbn=recognition_result["isbn"])
    
    if not metadata and recognition_result.get("title"):
        metadata = await fetch_book_metadata(
            title=recognition_result["title"],
            author=recognition_result.get("author")
        )
    
    # 合并结果
    result = {**recognition_result}
    if metadata:
        # 如果元数据有更完整的信息，使用元数据
        for key in ["title", "author", "publisher", "publish_date", "isbn", "cover_image", "description", "category"]:
            if metadata.get(key) and (not result.get(key) or len(str(metadata[key])) > len(str(result.get(key, "")))):
                result[key] = metadata[key]
    
    # 添加图片URL
    result["image_url"] = f"/data/uploads/{file_name}"
    
    return result
