"""SQLAlchemy persistence models for the MySQL Habit Tracker schema."""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, Date, ForeignKey, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy persistence models."""


class UserRecord(Base):
    """Persistent user account with a bcrypt password hash."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


class HabitRecord(Base):
    """Persistent habit owned by exactly one user."""

    __tablename__ = "habit"
    __table_args__ = (UniqueConstraint("id", "id_user", name="uq_habit_id_user"),)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    id_user: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.id", name="fk_habit_user", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )


class HabitLogRecord(Base):
    """Persistent daily duration log constrained to its habit owner."""

    __tablename__ = "habit_log"
    __table_args__ = (
        CheckConstraint("habit_duration >= 0", name="chk_habit_log_duration"),
        ForeignKeyConstraint(
            ["id_habit", "id_user"],
            ["habit.id", "habit.id_user"],
            name="fk_habit_log_habit_owner",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["id_user"],
            ["user.id"],
            name="fk_habit_log_user",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    id_habit: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True)
    id_user: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False, index=True)
    habit_duration: Mapped[int] = mapped_column(INTEGER(unsigned=True), nullable=False, default=60, server_default="60")
    log_date: Mapped[date] = mapped_column(Date, primary_key=True)