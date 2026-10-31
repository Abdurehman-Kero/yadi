import uuid

from sqlalchemy import Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from yadi.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text)
