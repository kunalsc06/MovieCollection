from pathlib import Path
import sqlite3
from typing import Any


DATABASE_PATH = Path(__file__).with_name("movies.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tmdb_id INTEGER UNIQUE,
                movie_name TEXT NOT NULL,
                genre TEXT NOT NULL,
                rating REAL NOT NULL CHECK (rating >= 0 AND rating <= 10),
                release_year INTEGER NOT NULL CHECK (release_year >= 1888),
                overview TEXT,
                poster_path TEXT,
                vote_count INTEGER
            )
            """
        )
        existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(movies)")}
        optional_columns = {
            "tmdb_id": "INTEGER",
            "overview": "TEXT",
            "poster_path": "TEXT",
            "vote_count": "INTEGER",
        }
        for column_name, column_type in optional_columns.items():
            if column_name not in existing_columns:
                connection.execute(f"ALTER TABLE movies ADD COLUMN {column_name} {column_type}")
        connection.execute(
            """
            DELETE FROM movies
            WHERE tmdb_id IS NOT NULL
              AND movie_id NOT IN (
                  SELECT MIN(movie_id)
                  FROM movies
                  WHERE tmdb_id IS NOT NULL
                  GROUP BY tmdb_id
              )
            """
        )
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_movies_tmdb_id ON movies(tmdb_id)")


def add_movie(movie_name: str, genre: str, rating: float, release_year: int) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO movies (movie_name, genre, rating, release_year)
            VALUES (?, ?, ?, ?)
            """,
            (movie_name.strip(), genre, rating, release_year),
        )


def add_tmdb_movie(movie: dict[str, Any]) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO movies
                (tmdb_id, movie_name, genre, rating, release_year, overview, poster_path, vote_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                movie["tmdb_id"],
                movie["movie_name"],
                movie["genre"],
                movie["rating"],
                movie["release_year"],
                movie["overview"],
                movie["poster_path"],
                movie["vote_count"],
            ),
        )
    return cursor.rowcount == 1


def get_movies() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT movie_id, movie_name, genre, rating, release_year
            FROM movies
            ORDER BY rating DESC, movie_name COLLATE NOCASE
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_average_rating() -> float | None:
    with get_connection() as connection:
        result = connection.execute("SELECT AVG(rating) AS average_rating FROM movies").fetchone()
    return result["average_rating"] if result["average_rating"] is not None else None


def get_highest_rated_movie() -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT movie_id, movie_name, genre, rating, release_year
            FROM movies
            ORDER BY rating DESC, movie_name COLLATE NOCASE
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def get_genre_summary() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT genre, COUNT(*) AS movie_count, ROUND(AVG(rating), 2) AS average_rating
            FROM movies
            GROUP BY genre
            ORDER BY movie_count DESC, genre COLLATE NOCASE
            """
        ).fetchall()
    return [dict(row) for row in rows]