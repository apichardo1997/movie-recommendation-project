from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import BaseSQLModel


class MovieGenreModel(BaseSQLModel):
    __tablename__ = "movie_genre"

    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("genres.id"), primary_key=True, index=True
    )
