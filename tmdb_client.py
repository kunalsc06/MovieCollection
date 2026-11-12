# Checked by Kunal S C
from typing import Any
import time

import requests
import truststore


truststore.inject_into_ssl()


TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w342"


class TMDBError(RuntimeError):
    pass


def _request(path: str, access_token: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    last_error: requests.RequestException | None = None
    for attempt in range(3):
        try:
            response = requests.get(
                f"{TMDB_API_URL}{path}",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as error:
            if error.response is not None and error.response.status_code in (401, 403):
                raise TMDBError("TMDB rejected the token. Check that you used a current API Read Access Token.") from error
            raise TMDBError(f"TMDB returned HTTP {error.response.status_code if error.response is not None else 'error'}.") from error
        except requests.RequestException as error:
            last_error = error
            if attempt < 2:
                time.sleep(0.5)
    raise TMDBError("TMDB connection failed after 3 attempts. Check your network connection.") from last_error


def search_movies(query: str, access_token: str) -> list[dict[str, Any]]:
    payload = _request("/search/movie", access_token, {"query": query, "include_adult": "false"})
    return payload.get("results", [])


def get_movie_details(movie_id: int, access_token: str) -> dict[str, Any]:
    return _request(f"/movie/{movie_id}", access_token)


def to_movie_record(movie: dict[str, Any]) -> dict[str, Any]:
    release_date = movie.get("release_date") or ""
    genres = movie.get("genres") or []
    return {
        "tmdb_id": movie["id"],
        "movie_name": movie.get("title") or movie.get("original_title") or "Untitled",
        "genre": ", ".join(genre["name"] for genre in genres) or "Other",
        "rating": round(float(movie.get("vote_average") or 0), 1),
        "release_year": int(release_date[:4]) if release_date[:4].isdigit() else 1888,
        "overview": movie.get("overview") or "No overview available.",
        "poster_path": movie.get("poster_path"),
        "vote_count": int(movie.get("vote_count") or 0),
    }