from sqlalchemy.orm import Mapped, mapped_column

from server.models.base import BaseSQLModel


class MoviesRawModel(BaseSQLModel):
    __tablename__ = "movies_raw"

    movieId: Mapped[int] = mapped_column(
        primary_key=True
    )  # primary key necessary for sqlalchemy
    title: Mapped[str] = mapped_column()
    genres: Mapped[str] = mapped_column()
