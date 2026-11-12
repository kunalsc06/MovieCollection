<!-- Checked by Kunal S C -->
# Reel Shelf

A Streamlit movie collection manager backed by SQLite. Add films, browse the collection, track ratings, identify the highest-rated film, and compare genres.

## Setup

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

The app creates `movies.db` and its `movies` table automatically on first run. The database is intentionally ignored by Git because it contains personal collection data.

## TMDB integration

The app can search TMDB and save selected movie details locally. Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example` and add a regenerated TMDB API Read Access Token. Never commit that file or place the token directly in Python code.

Alternatively, set `TMDB_ACCESS_TOKEN` as an environment variable before starting Streamlit. The integration uses TMDB's official `/search/movie` and `/movie/{id}` endpoints and stores the title, genres, rating, release year, overview, poster path, vote count, and TMDB ID in SQLite.

## Git

```powershell
git init
git add .
git commit -m "Build movie collection manager"
```

## Features

- Add a movie with name, genre, rating, and release year.
- View all movies sorted by rating.
- See the collection average rating.
- See the highest-rated movie.
- See film counts and average ratings by genre.