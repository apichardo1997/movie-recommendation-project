from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import BaseSQLModel


class GenreModel(BaseSQLModel):
    __tablename__ = "genres"

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    genre_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
