"""数据库迁移

由于项目使用 create_all() 而非 Alembic, 需要手动处理 schema 变更.
每个迁移步骤独立检测, 确保增量变更不会遗漏.
"""

import logging
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

logger = logging.getLogger("bookworm.migrate")


def _safe_add_column(db: Session, table: str, column_def: str, col_name: str):
    """安全地添加列 (如果已存在则跳过)"""
    try:
        db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
        logger.info(f"  + {table}.{col_name}")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            logger.debug(f"  = {table}.{col_name} 已存在, 跳过")
        else:
            raise


def _has_column(inspector, table: str, col: str) -> bool:
    """检查表中是否存在某列"""
    if table not in inspector.get_table_names():
        return False
    columns = [c["name"] for c in inspector.get_columns(table)]
    return col in columns


def migrate_db(db: Session):
    """逐项检查并执行数据库迁移"""
    inspector = inspect(db.bind)

    changed = False

    # ── users 表 ──
    if "users" in inspector.get_table_names():
        if not _has_column(inspector, "users", "user_id"):
            logger.info("迁移: users 添加 user_id / phone / password_hash / is_anonymous / updated_at")
            _safe_add_column(db, "users", "user_id VARCHAR(36)", "user_id")
            _safe_add_column(db, "users", "phone VARCHAR(20)", "phone")
            _safe_add_column(db, "users", "password_hash VARCHAR(128)", "password_hash")
            _safe_add_column(db, "users", "is_anonymous BOOLEAN DEFAULT 1", "is_anonymous")
            _safe_add_column(db, "users", "updated_at DATETIME", "updated_at")
            changed = True
    else:
        logger.info("users 表不存在, 将由 create_all 创建")

    # ── books 表 ──
    if "books" in inspector.get_table_names():
        if not _has_column(inspector, "books", "user_id"):
            logger.info("迁移: books 添加 user_id")
            _safe_add_column(db, "books", "user_id VARCHAR(36)", "user_id")
            changed = True
        if not _has_column(inspector, "books", "started_at"):
            logger.info("迁移: books 添加 started_at")
            _safe_add_column(db, "books", "started_at DATETIME", "started_at")
            changed = True

    # ── reading_records 表 ──
    if "reading_records" in inspector.get_table_names():
        if not _has_column(inspector, "reading_records", "user_id"):
            logger.info("迁移: reading_records 添加 user_id")
            _safe_add_column(db, "reading_records", "user_id VARCHAR(36)", "user_id")
            changed = True

    # ── 数据填充: 将现有数据关联到默认匿名用户 ──
    if changed:
        _fill_default_user(db)

    # ── 索引 ──
    db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_user_id ON users (user_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_books_user_id ON books (user_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_reading_records_user_id ON reading_records (user_id)"))

    db.commit()
    logger.info("迁移完成")


def _fill_default_user(db: Session):
    """确保所有 user_id 为空的行关联到一个默认匿名用户"""
    import uuid

    # 查找或创建默认用户
    result = db.execute(text("SELECT user_id FROM users WHERE user_id IS NOT NULL LIMIT 1"))
    existing = result.fetchone()

    if existing:
        default_user_id = existing[0]
    else:
        default_user_id = str(uuid.uuid4())
        db.execute(
            text("INSERT INTO users (user_id, name, is_anonymous, created_at) VALUES (:uid, :name, :anon, datetime('now'))"),
            {"uid": default_user_id, "name": "书架主人", "anon": 1}
        )
        logger.info(f"  创建默认匿名用户: {default_user_id}")

    # 回填
    db.execute(text("UPDATE books SET user_id = :uid WHERE user_id IS NULL"), {"uid": default_user_id})
    db.execute(text("UPDATE reading_records SET user_id = :uid WHERE user_id IS NULL"), {"uid": default_user_id})
