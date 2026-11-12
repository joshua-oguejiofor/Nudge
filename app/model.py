import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db
from .utility import TaskPriority


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    password: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(120), unique=True, nullable=False)


    todo: Mapped["Todo"] = relationship(back_populates="user", cascade="all, delete-orphan")


class Todo(db.Model):
    __tablename__ = "todo_list"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    completed: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(
        sa.Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM,
    )
    
    user: Mapped["User"] = relationship(back_populates="todo")
    