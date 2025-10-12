from models.base import BaseSQLModel
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(BaseSQLModel):
    __table__ = "users"

    id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column()
