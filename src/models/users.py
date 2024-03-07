import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.postgres import Base


users_roles_table = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=users_roles_table, back_populates="users", cascade="all, delete"
    )

    login_histories: Mapped[list["LoginHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin", order_by="LoginHistory.created_at"
    )

    def __repr__(self) -> str:
        return f"<User {self.id!r}>"


class LoginHistory(Base):
    __tablename__ = "login_histories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    useragent: Mapped[str] = mapped_column(String(length=512))
    remote_addr: Mapped[str] = mapped_column(String(length=100))
    referer: Mapped[str] = mapped_column(String(length=255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="login_histories")

    def __repr__(self) -> str:
        return f"<LoginHistory {self.id!r}>"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title: Mapped[str] = mapped_column(String(length=255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(length=1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(
        User, secondary=users_roles_table, back_populates="roles", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<LoginHistory {self.id!r}>"
