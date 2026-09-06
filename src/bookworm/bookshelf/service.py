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
    
    def get_all_books(self) -> List[Book]:
        """获取所有书籍"""
        return self.db.query(Book).order_by(Book.created_at.desc()).all()
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """根据ID获取书籍"""
        return self.db.query(Book).filter(Book.id == book_id).first()
    
    def get_books_by_status(self, status: ReadingStatus) -> List[Book]:
        """根据状态获取书籍"""
        return self.db.query(Book).filter(Book.user_status == status).all()
    
    def add_book(self, book_data: Dict[str, Any]) -> Book:
        """添加书籍"""
        book = Book(
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
    
    def update_book(self, book_id: int, book_data: Dict[str, Any]) -> Optional[Book]:
        """更新书籍"""
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        for key, value in book_data.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        self.db.commit()
        self.db.refresh(book)
        return book
    
    def update_reading_status(self, book_id: int, status: ReadingStatus) -> Optional[Book]:
        """更新阅读状态"""
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        book.user_status = status
        if status == ReadingStatus.FINISHED:
            book.finished_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(book)
        return book
    
    def delete_book(self, book_id: int) -> bool:
        """删除书籍"""
        book = self.get_book_by_id(book_id)
        if not book:
            return False
        
        self.db.delete(book)
        self.db.commit()
        return True
    
    def add_reading_record(self, book_id: int, record_data: Dict[str, Any]) -> Optional[ReadingRecord]:
        """添加阅读记录"""
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        record = ReadingRecord(
            book_id=book_id,
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
    
    def get_all_records(self) -> List[ReadingRecord]:
        """获取所有阅读记录（按时间排序）"""
        return self.db.query(ReadingRecord)\
            .order_by(ReadingRecord.created_at.desc())\
            .all()
    
    def search_books(self, keyword: str) -> List[Book]:
        """搜索书籍"""
        return self.db.query(Book)\
            .filter(
                (Book.title.contains(keyword)) |
                (Book.author.contains(keyword))
            )\
            .all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取阅读统计"""
        total_books = self.db.query(func.count(Book.id)).scalar()
        
        # 各状态数量
        want_to_read = self.db.query(func.count(Book.id))\
            .filter(Book.user_status == ReadingStatus.WANT_TO_READ)\
            .scalar()
        reading = self.db.query(func.count(Book.id))\
            .filter(Book.user_status == ReadingStatus.READING)\
            .scalar()
        finished = self.db.query(func.count(Book.id))\
            .filter(Book.user_status == ReadingStatus.FINISHED)\
            .scalar()
        
        # 总记录数
        total_records = self.db.query(func.count(ReadingRecord.id)).scalar()
        
        # 书架年龄
        user = self.db.query(User).first()
        if not user:
            user = User(name="书架主人")
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        shelf_age_days = (datetime.now() - user.created_at).days
        
        return {
            "total_books": total_books,
            "want_to_read": want_to_read,
            "reading": reading,
            "finished": finished,
            "total_records": total_records,
            "shelf_age_days": shelf_age_days
        }
