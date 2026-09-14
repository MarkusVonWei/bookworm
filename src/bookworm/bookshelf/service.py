"""书架服务层"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Book, ReadingRecord, ReadingStatus, User


class BookshelfService:
    """书架服务"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 书籍操作 (用户隔离) ==========

    def get_books_by_user(self, user_id: str) -> List[Book]:
        """获取用户的所有书籍"""
        return self.db.query(Book)\
            .filter(Book.user_id == user_id)\
            .order_by(Book.created_at.desc())\
            .all()

    def get_book_by_id_and_user(self, book_id: int, user_id: str) -> Optional[Book]:
        """根据ID获取书籍 (用户隔离)"""
        return self.db.query(Book)\
            .filter(Book.id == book_id, Book.user_id == user_id)\
            .first()

    def get_books_by_user_and_status(self, user_id: str, status: ReadingStatus) -> List[Book]:
        """根据状态获取用户书籍"""
        return self.db.query(Book)\
            .filter(Book.user_id == user_id, Book.user_status == status)\
            .all()

    def add_book(self, book_data: Dict[str, Any]) -> Book:
        """添加书籍"""
        book = Book(
            user_id=book_data["user_id"],
            title=book_data["title"],
            author=book_data.get("author"),
            publisher=book_data.get("publisher"),
            publish_date=book_data.get("publish_date"),
            isbn=book_data.get("isbn"),
            cover_image=book_data.get("cover_image"),
            description=book_data.get("description"),
            category=book_data.get("category"),
            user_status=book_data.get("user_status", ReadingStatus.WANT_TO_READ)
        )
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update_book(self, book_id: int, book_data: Dict[str, Any], user_id: str) -> Optional[Book]:
        """更新书籍 (用户隔离)"""
        book = self.get_book_by_id_and_user(book_id, user_id)
        if not book:
            return None

        for key, value in book_data.items():
            if key != "user_id" and hasattr(book, key):
                setattr(book, key, value)

        self.db.commit()
        self.db.refresh(book)
        return book

    def update_reading_status(self, book_id: int, status: ReadingStatus, user_id: str) -> Optional[Book]:
        """更新阅读状态 (用户隔离)"""
        book = self.get_book_by_id_and_user(book_id, user_id)
        if not book:
            return None

        book.user_status = status
        if status == ReadingStatus.READING and not book.started_at:
            book.started_at = datetime.now()
        if status == ReadingStatus.FINISHED:
            book.finished_at = datetime.now()

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete_book(self, book_id: int, user_id: str) -> bool:
        """删除书籍 (用户隔离)"""
        book = self.get_book_by_id_and_user(book_id, user_id)
        if not book:
            return False

        self.db.delete(book)
        self.db.commit()
        return True

    # ========== 阅读记录操作 ==========

    def add_reading_record(self, book_id: int, record_data: Dict[str, Any], user_id: str) -> Optional[ReadingRecord]:
        """添加阅读记录"""
        book = self.get_book_by_id_and_user(book_id, user_id)
        if not book:
            return None

        record = ReadingRecord(
            book_id=book_id,
            user_id=user_id,
            content=record_data.get("content"),
            excerpt=record_data.get("excerpt"),
            page_number=record_data.get("page_number"),
            tags=record_data.get("tags")
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_reading_records(self, book_id: int) -> List[ReadingRecord]:
        """获取书籍的所有阅读记录"""
        return self.db.query(ReadingRecord)\
            .filter(ReadingRecord.book_id == book_id)\
            .order_by(ReadingRecord.created_at.desc())\
            .all()

    def get_all_records_by_user(self, user_id: str) -> List[ReadingRecord]:
        """获取用户的所有阅读记录 (按时间排序)"""
        return self.db.query(ReadingRecord)\
            .filter(ReadingRecord.user_id == user_id)\
            .order_by(ReadingRecord.created_at.desc())\
            .all()

    # ========== 时间线 ==========

    def get_timeline(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的时间线: 书籍状态变更里程碑 + 阅读记录, 按时间倒序"""
        events = []

        # 1. 从书籍模型生成状态里程碑
        books = self.db.query(Book).filter(Book.user_id == user_id).all()
        for book in books:
            # 添加到想读
            events.append({
                "type": "milestone",
                "milestone": "added",
                "book_id": book.id,
                "book_title": book.title,
                "timestamp": book.created_at,
            })
            # 开始阅读
            if book.started_at:
                events.append({
                    "type": "milestone",
                    "milestone": "started",
                    "book_id": book.id,
                    "book_title": book.title,
                    "timestamp": book.started_at,
                })
            # 阅读完成
            if book.finished_at:
                events.append({
                    "type": "milestone",
                    "milestone": "finished",
                    "book_id": book.id,
                    "book_title": book.title,
                    "timestamp": book.finished_at,
                })

        # 2. 阅读记录
        records = self.db.query(ReadingRecord)\
            .filter(ReadingRecord.user_id == user_id)\
            .all()
        for record in records:
            book = self.get_book_by_id_and_user(record.book_id, user_id)
            events.append({
                "type": "record",
                "id": record.id,
                "book_id": record.book_id,
                "book_title": book.title if book else "未知书籍",
                "content": record.content,
                "excerpt": record.excerpt,
                "page_number": record.page_number,
                "tags": record.tags,
                "timestamp": record.created_at,
            })

        # 按时间倒序排列
        events.sort(key=lambda e: e["timestamp"], reverse=True)
        return events

    # ========== 搜索 ==========

    def search_books_by_user(self, keyword: str, user_id: str) -> List[Book]:
        """搜索用户书籍"""
        return self.db.query(Book)\
            .filter(
                Book.user_id == user_id,
                (Book.title.contains(keyword)) |
                (Book.author.contains(keyword))
            )\
            .all()

    # ========== 统计 ==========

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户阅读统计"""
        total_books = self.db.query(func.count(Book.id))\
            .filter(Book.user_id == user_id)\
            .scalar()

        want_to_read = self.db.query(func.count(Book.id))\
            .filter(Book.user_id == user_id, Book.user_status == ReadingStatus.WANT_TO_READ)\
            .scalar()

        reading = self.db.query(func.count(Book.id))\
            .filter(Book.user_id == user_id, Book.user_status == ReadingStatus.READING)\
            .scalar()

        finished = self.db.query(func.count(Book.id))\
            .filter(Book.user_id == user_id, Book.user_status == ReadingStatus.FINISHED)\
            .scalar()

        total_records = self.db.query(func.count(ReadingRecord.id))\
            .filter(ReadingRecord.user_id == user_id)\
            .scalar()

        user = self.db.query(User).filter(User.user_id == user_id).first()
        shelf_age_days = (datetime.now() - user.created_at).days if user else 0

        return {
            "total_books": total_books,
            "want_to_read": want_to_read,
            "reading": reading,
            "finished": finished,
            "total_records": total_records,
            "shelf_age_days": shelf_age_days
        }
