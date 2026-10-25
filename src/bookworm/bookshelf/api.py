"""书架API接口"""

import os
import uuid
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from ..database import get_db
from .models import Book, ReadingRecord, ReadingStatus, User
from .service import BookshelfService
from .user_service import get_or_create_anonymous_user, register_user, login_user
from .recognition import recognize_book_from_image, fetch_book_metadata

router = APIRouter(prefix="/api", tags=["书架"])

# 上传目录
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ========== 依赖注入 ==========

def get_current_user(
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """从 X-User-Id header 获取当前用户, 不存在则 401"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="缺少 X-User-Id header")
    user = db.query(User).filter(User.user_id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在, 请先初始化")
    return user


# ========== 用户相关模型 ==========

class UserInitRequest(BaseModel):
    device_id: str


class UserInitResponse(BaseModel):
    user_id: str
    name: str
    is_anonymous: bool
    created_at: datetime


class RegisterRequest(BaseModel):
    phone: str
    password: str
    name: str = "书架主人"


class LoginRequest(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    name: str
    phone: str
    is_anonymous: bool


# ========== 用户API ==========

@router.post("/user/init", response_model=UserInitResponse)
def init_user(req: UserInitRequest, db: Session = Depends(get_db)):
    """初始化匿名用户 - 首次访问时调用, 根据 device_id 创建或返回已有用户"""
    user = get_or_create_anonymous_user(db, req.device_id)
    return UserInitResponse(
        user_id=user.user_id,
        name=user.name,
        is_anonymous=user.is_anonymous,
        created_at=user.created_at,
    )


@router.post("/user/register", response_model=LoginResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册正式用户 - 需要 header 中的 X-User-Id (匿名用户的 device_id)"""
    # 这里不能用 get_current_user 依赖, 因为注册时可能还没有完整用户
    # 但我们需要知道是哪个匿名用户在注册
    # 通过另一种方式: 注册请求本身携带 device_id
    # 为了简化, 注册接口不需要 X-User-Id, 而是通过 device_id 参数
    # 但用户说"注册后把匿名用户数据转成正式用户", 所以需要 X-User-Id
    # 这里我们改为: 注册时也传 X-User-Id header
    raise HTTPException(status_code=400, detail="请使用 /api/user/register-with-device 接口")


class RegisterWithDeviceRequest(BaseModel):
    device_id: str
    phone: str
    password: str
    name: str = "书架主人"


@router.post("/user/register-with-device", response_model=LoginResponse)
def register_with_device(req: RegisterWithDeviceRequest, db: Session = Depends(get_db)):
    """注册正式用户 (携带 device_id) - 将匿名用户升级为正式用户"""
    try:
        user = register_user(db, req.device_id, req.phone, req.password, req.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LoginResponse(
        user_id=user.user_id,
        name=user.name,
        phone=user.phone,
        is_anonymous=user.is_anonymous,
    )


@router.post("/user/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录"""
    user = login_user(db, req.phone, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    return LoginResponse(
        user_id=user.user_id,
        name=user.name,
        phone=user.phone,
        is_anonymous=user.is_anonymous,
    )


@router.get("/user/me", response_model=UserInitResponse)
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInitResponse(
        user_id=user.user_id,
        name=user.name,
        is_anonymous=user.is_anonymous,
        created_at=user.created_at,
    )


# ========== 书籍相关模型 ==========

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

    @field_validator("page_number", mode="before")
    @classmethod
    def coerce_page_number(cls, v):
        if v == "" or v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


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


# ========== 书籍API (用户隔离) ==========

@router.get("/bookshelf/books", response_model=List[BookResponse])
def get_books(
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有书籍"""
    service = BookshelfService(db)

    if status:
        try:
            reading_status = ReadingStatus(status)
            books = service.get_books_by_user_and_status(user.user_id, reading_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    else:
        books = service.get_books_by_user(user.user_id)

    result = []
    for book in books:
        records_count = len(service.get_reading_records(book.id))
        book_dict = BookResponse.model_validate(book)
        book_dict.records_count = records_count
        result.append(book_dict)

    return result


@router.get("/bookshelf/books/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单本书籍"""
    service = BookshelfService(db)
    book = service.get_book_by_id_and_user(book_id, user.user_id)

    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    records_count = len(service.get_reading_records(book.id))
    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = records_count

    return book_dict


@router.post("/bookshelf/books", response_model=BookResponse)
def create_book(
    book_data: BookCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加书籍"""
    service = BookshelfService(db)

    try:
        status = ReadingStatus(book_data.user_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")

    book_dict = book_data.model_dump()
    book_dict["user_status"] = status
    book_dict["user_id"] = user.user_id

    try:
        book = service.add_book(book_dict)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = 0

    return book_dict


@router.put("/bookshelf/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新书籍"""
    service = BookshelfService(db)

    book_dict = book_data.model_dump(exclude_unset=True)

    if "user_status" in book_dict:
        try:
            book_dict["user_status"] = ReadingStatus(book_dict["user_status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")

    book = service.update_book(book_id, book_dict, user.user_id)

    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    records_count = len(service.get_reading_records(book.id))
    book_dict = BookResponse.model_validate(book)
    book_dict.records_count = records_count

    return book_dict


@router.delete("/bookshelf/books/{book_id}")
def delete_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除书籍"""
    service = BookshelfService(db)

    if not service.delete_book(book_id, user.user_id):
        raise HTTPException(status_code=404, detail="书籍不存在")

    return {"message": "删除成功"}


@router.put("/bookshelf/books/{book_id}/status")
def update_reading_status(
    book_id: int,
    status: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新阅读状态"""
    service = BookshelfService(db)

    try:
        reading_status = ReadingStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")

    book = service.update_reading_status(book_id, reading_status, user.user_id)

    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    return {"message": "状态更新成功", "status": status}


@router.get("/bookshelf/books/{book_id}/records", response_model=List[ReadingRecordResponse])
def get_reading_records(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取书籍的阅读记录"""
    service = BookshelfService(db)

    book = service.get_book_by_id_and_user(book_id, user.user_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    records = service.get_reading_records(book.id)
    return records


@router.post("/bookshelf/books/{book_id}/records", response_model=ReadingRecordResponse)
def create_reading_record(
    book_id: int,
    record_data: ReadingRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加阅读记录"""
    service = BookshelfService(db)

    record = service.add_reading_record(book_id, record_data.model_dump(), user.user_id)

    if not record:
        raise HTTPException(status_code=404, detail="书籍不存在")

    return record


@router.get("/bookshelf/records", response_model=List[ReadingRecordResponse])
def get_all_records(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有阅读记录"""
    service = BookshelfService(db)
    return service.get_all_records_by_user(user.user_id)


@router.get("/bookshelf/search", response_model=List[BookResponse])
def search_books(
    keyword: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """搜索当前用户的书籍"""
    service = BookshelfService(db)
    books = service.search_books_by_user(keyword, user.user_id)

    result = []
    for book in books:
        records_count = len(service.get_reading_records(book.id))
        book_dict = BookResponse.model_validate(book)
        book_dict.records_count = records_count
        result.append(book_dict)

    return result


@router.get("/bookshelf/search-external")
async def search_books_external(
    keyword: str,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    """搜索外部书籍目录（豆瓣）用于添加新书"""
    from .recognition import search_books_external as _search
    results = await _search(keyword, limit)
    return results


@router.get("/bookshelf/timeline")
def get_timeline(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的时间线 (状态变更里程碑 + 阅读记录)"""
    service = BookshelfService(db)
    return service.get_timeline(user.user_id)


@router.get("/bookshelf/statistics", response_model=StatisticsResponse)
def get_statistics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的统计信息"""
    service = BookshelfService(db)
    return service.get_statistics(user.user_id)


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
    image_url: str


@router.post("/bookshelf/recognize", response_model=RecognizeResponse)
async def recognize_book(file: UploadFile = File(...)):
    """
    识别书籍

    上传书籍封面图片，使用VL大模型识别书籍信息
    """
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    file_ext = Path(file.filename or "").suffix or ".jpg"
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # 步骤1: 识别（优先条形码，备选 VLM）
    recognition_result = await recognize_book_from_image(str(file_path))

    if "error" in recognition_result:
        raise HTTPException(status_code=500, detail=recognition_result["error"])

    logger.info(f"[识别] 识别结果: source={recognition_result.get('source', 'vlm')}, isbn={recognition_result.get('isbn')}, title={recognition_result.get('title')}")

    # 步骤2: 查询元数据（使用 ISBN 优先，标题备选）
    metadata = None
    try:
        if recognition_result.get("isbn"):
            logger.info(f"[识别] 使用 ISBN 查询元数据: {recognition_result['isbn']}")
            metadata = await asyncio.wait_for(
                fetch_book_metadata(isbn=recognition_result["isbn"]),
                timeout=8.0
            )
        if not metadata and recognition_result.get("title"):
            logger.info(f"[识别] 使用标题查询元数据: {recognition_result['title']}")
            metadata = await asyncio.wait_for(
                fetch_book_metadata(
                    title=recognition_result["title"],
                    author=recognition_result.get("author")
                ),
                timeout=8.0
            )
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"[识别] metadata获取失败/超时: {e}, 使用识别结果")

    # 步骤2.5: 如果条形码识别到 ISBN，确保返回
    if recognition_result.get("source") == "barcode" and recognition_result.get("isbn"):
        logger.info(f"[识别] 条形码识别到 ISBN: {recognition_result['isbn']}, 即使无元数据也返回")

    # 步骤3: 合并结果（元数据补充识别结果）
    result = {**recognition_result}
    if metadata:
        for key in ["title", "author", "publisher", "publish_date", "isbn", "cover_image", "description", "category"]:
            if metadata.get(key) and (not result.get(key) or len(str(metadata[key])) > len(str(result.get(key, "")))):
                result[key] = metadata[key]

    # 步骤4: 添加图片 URL
    result["image_url"] = f"/data/uploads/{file_name}"

    logger.info(f"[识别] 最终结果: title={result.get('title')}, author={result.get('author')}, isbn={result.get('isbn')}")

    return result
