from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base import BaseSQLModel

if TYPE_CHECKING:
    from server.models.movies import MovieModel
    from server.models.user import UserModel

else:
    MovieModel = "MovieModel"
    UserModel = "UserModel"


class RatingModel(BaseSQLModel):
    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint("rating >= 0.5 AND rating <= 5.0"),
        UniqueConstraint("user_id", "movie_id"),
    )

    #WHY: Map rating_id attribute to the 'id' column in the database
    rating_id: Mapped[int] = mapped_column(
        "id", Integer, primary_key=True, autoincrement=True
    )
    #WHY: Foreign key references users.id (the actual database column name)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False, index=True
    )
    rating: Mapped[float] = mapped_column(Numeric(2, 1), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    user: Mapped[UserModel] = relationship(back_populates="ratings")
    movie: Mapped[MovieModel] = relationship(back_populates="ratings")
