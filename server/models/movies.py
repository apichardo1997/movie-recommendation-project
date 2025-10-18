from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import BaseSQLModel


class MovieModel(BaseSQLModel):
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
