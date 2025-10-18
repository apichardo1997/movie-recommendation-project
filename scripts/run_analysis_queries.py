import logging
import sys
from pathlib import Path

sys.path.append(".")

from sqlalchemy import desc, extract, func, select

from server.backend.postgres import PostgresSessionManager
from server.models import (
    GenreModel,
    MovieGenreModel,
    MovieModel,
    RatingModel,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

session_manager = PostgresSessionManager()


def query_top_genres_by_rating():
    """Top 10 highest-ranking genres by average rating."""
    with session_manager.open_session() as session:
        query = (
            select(
                GenreModel.genre_name, func.avg(RatingModel.rating).label("avg_rating")
            )
            .join(MovieGenreModel, GenreModel.genre_id == MovieGenreModel.genre_id)
            .join(MovieModel, MovieGenreModel.movie_id == MovieModel.movie_id)
            .join(RatingModel, MovieModel.movie_id == RatingModel.movie_id)
            .group_by(GenreModel.genre_name)
            .order_by(desc(func.avg(RatingModel.rating)))
            .limit(10)
        )

        return session.execute(query).all()


def query_most_polarizing_movies(min_ratings: int = 1000):
    """10 most polarizing movies by standard deviation."""
    with session_manager.open_session() as session:
        query = (
            select(
                MovieModel.title, func.stddev(RatingModel.rating).label("rating_stddev")
            )
            .join(RatingModel, MovieModel.movie_id == RatingModel.movie_id)
            .group_by(MovieModel.movie_id, MovieModel.title)
            .having(func.count(RatingModel.rating) >= min_ratings)
            .order_by(desc("rating_stddev"))
            .limit(10)
        )

        return session.execute(query).all()


def query_monthly_ratings_timeseries():
    """Monthly count of ratings time series."""
    with session_manager.open_session() as session:
        query = (
            select(
                extract("year", RatingModel.timestamp).label("year"),
                extract("month", RatingModel.timestamp).label("month"),
                func.count(RatingModel.rating_id).label("rating_count"),
            )
            .group_by(
                extract("year", RatingModel.timestamp),
                extract("month", RatingModel.timestamp),
            )
            .order_by("year", "month")
        )

        return session.execute(query).all()


def main():
    """Run queries and write results to markdown."""
    output_dir = Path("scripts/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "analysis_queries_results.md"

    with open(output_file, "w") as f:
        f.write("# Analysis Query Results\n\n")

        # Query 1: Top genres
        f.write("## 1. Top 10 Highest-Ranking Genres by Average Rating\n\n")
        results1 = query_top_genres_by_rating()
        for i, (genre, avg_rating) in enumerate(results1, 1):
            f.write(f"{i}. {genre}: {avg_rating:.3f}\n")

        # Query 2: Polarizing movies (try 1000, fallback to 100)
        f.write("\n## 2. Most Polarizing Movies by Standard Deviation\n\n")
        results2 = query_most_polarizing_movies(1000)
        if not results2:
            results2 = query_most_polarizing_movies(100)
            f.write("*(Using minimum 100 ratings)*\n\n")

        for i, (title, stddev) in enumerate(results2, 1):
            f.write(f"{i}. {title}: {stddev:.3f}\n")

        # Query 3: Monthly time series
        f.write("\n## 3. Monthly Ratings Time Series\n\n")
        results3 = query_monthly_ratings_timeseries()
        for year, month, count in results3:
            f.write(f"{int(year):04d}-{int(month):02d}: {count}\n")

    print(f"Results written to: {output_file}")


if __name__ == "__main__":
    main()
