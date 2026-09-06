"""书架数据模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class ReadingStatus(enum.Enum):
    """阅读状态"""
    WANT_TO_READ = "想读"  # 想读
    READING = "在读"  # 在读
    FINISHED = "已读"  # 已读


class Book(Base):
    """书籍模型"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    publish_date = Column(String(50), nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    cover_image = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # 用户相关字段
    user_status = Column(Enum(ReadingStatus), default=ReadingStatus.WANT_TO_READ, nullable=False)
    user_rating = Column(Float, nullable=True)  # 用户评分 1-5
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    finished_at = Column(DateTime, nullable=True)  # 完成阅读时间
    
    # 关联
    reading_records = relationship("ReadingRecord", back_populates="book", cascade="all, delete-orphan")


class ReadingRecord(Base):
    """阅读记录模型"""
    __tablename__ = "reading_records"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    # 记录内容
    content = Column(Text, nullable=True)  # 文字内容
    excerpt = Column(Text, nullable=True)  # 摘录
    page_number = Column(Integer, nullable=True)  # 页码
    tags = Column(String(500), nullable=True)  # 标签，逗号分隔
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # 关联
    book = relationship("Book", back_populates="reading_records")


class User(Base):
    """用户模型（简化版，MVP阶段单用户）"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="书架主人")
    created_at = Column(DateTime, default=datetime.now, nullable=False)  # 书架年龄
