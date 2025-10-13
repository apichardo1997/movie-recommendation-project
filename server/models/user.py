from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import BaseSQLModel


class UserModel(BaseSQLModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
