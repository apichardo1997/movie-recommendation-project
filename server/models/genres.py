from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import BaseSQLModel

if TYPE_CHECKING:
    from server.models.movies import MovieModel
else:
    MovieModel = "MovieModel"


class GenreModel(BaseSQLModel):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relationships
    movies: Mapped[list[MovieModel]] = relationship(
        secondary="movie_genre", back_populates="genres"
    )
