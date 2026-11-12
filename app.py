import os

import streamlit as st

from database import (
    add_movie,
    add_tmdb_movie,
    get_average_rating,
    get_genre_summary,
    get_highest_rated_movie,
    get_movies,
    initialize_database,
)
from tmdb_client import TMDBError, TMDB_IMAGE_URL, get_movie_details, search_movies, to_movie_record


st.set_page_config(page_title="Reel Shelf", page_icon="🎬", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #e7ece8; --muted: #94a49b; --night: #0e1413; --panel: #17201e; --panel-raised: #1d2926; --sage: #9cbea8; --amber: #d4a36a; --line: #2b3a35; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: radial-gradient(circle at 85% 0%, #1b2b26 0, var(--night) 35rem); }
    [data-testid="stAppViewContainer"] { background: transparent; }
    [data-testid="stHeader"] { background: rgba(14, 20, 19, .8); }
    [data-testid="stToolbar"] { right: 1rem; }
    label, .stMarkdown, p, span { color: var(--ink); }
    input, textarea, [data-baseweb="select"] > div { background: var(--panel-raised) !important; color: var(--ink) !important; border-color: var(--line) !important; }
    input:focus, textarea:focus { border-color: var(--sage) !important; box-shadow: 0 0 0 1px var(--sage) !important; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    h1 { font-size: clamp(2.4rem, 5vw, 4.8rem); line-height: .96; margin-bottom: .5rem; }
    h2 { font-size: 1.65rem; }
    .hero { border-bottom: 1px solid var(--line); padding: 2rem 0 2.4rem; margin-bottom: 2rem; }
    .eyebrow { color: var(--amber); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .hero-copy { color: var(--muted); font-size: 1.05rem; max-width: 38rem; }
    [data-testid="stMetric"] { background: rgba(23, 32, 30, .9); border: 1px solid var(--line); border-radius: 8px; padding: 1rem 1.1rem; }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--sage); font-family: 'Space Grotesk', sans-serif; }
    .section-label { color: var(--amber); font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 1.8rem 0 .7rem; }
    .spotlight { background: linear-gradient(145deg, #263d35, #17241f); color: var(--ink); border: 1px solid #3c5a4d; border-radius: 8px; padding: 1.35rem; min-height: 145px; }
    .spotlight small { color: var(--amber); font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    .spotlight h3 { margin: .35rem 0; color: var(--ink); }
    .spotlight p { color: #b7c8be; margin: 0; }
    .stButton > button, [data-testid="stFormSubmitButton"] > button { background: var(--sage); color: #102019; border: 1px solid var(--sage); border-radius: 6px; font-weight: 700; transition: background .2s ease, transform .2s ease; }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background: var(--amber); border-color: var(--amber); color: #1b1711; transform: translateY(-1px); }
    .stButton > button:focus, [data-testid="stFormSubmitButton"] > button:focus { box-shadow: 0 0 0 2px var(--night), 0 0 0 4px var(--amber); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
    [data-testid="stForm"] { background: rgba(23, 32, 30, .65); border: 1px solid var(--line); border-radius: 8px; padding: 1rem; }
    [data-testid="stAlert"] { background: var(--panel-raised); border-color: var(--line); color: var(--ink); }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_database()
movies = get_movies()
average_rating = get_average_rating()
top_movie = get_highest_rated_movie()

st.markdown(
    '<div class="hero"><div class="eyebrow">Personal film archive</div><h1>Reel Shelf</h1><div class="hero-copy">A calm, searchable home for the films worth remembering.</div></div>',
    unsafe_allow_html=True,
)


def get_tmdb_access_token() -> str | None:
    token = os.getenv("TMDB_ACCESS_TOKEN")
    try:
        token = token or st.secrets.get("TMDB_ACCESS_TOKEN")
    except (FileNotFoundError, KeyError):
        pass
    return token


st.markdown('<div class="section-label">Find a movie on TMDB</div>', unsafe_allow_html=True)
tmdb_token = get_tmdb_access_token()
with st.form("tmdb_search_form"):
    search_columns = st.columns([4, 1])
    search_query = search_columns[0].text_input("Search TMDB", placeholder="Try: The Matrix")
    search_submitted = search_columns[1].form_submit_button("Search", type="primary")

if st.button("Clear search results", key="clear_tmdb_results", type="secondary"):
    st.session_state["tmdb_results"] = []
    st.rerun()

if search_submitted:
    if not tmdb_token:
        st.error("TMDB is not configured. Add TMDB_ACCESS_TOKEN to Streamlit secrets or your environment.")
    elif not search_query.strip():
        st.warning("Enter a movie title to search.")
    else:
        try:
            st.session_state["tmdb_results"] = search_movies(search_query.strip(), tmdb_token)
        except TMDBError as error:
            st.error(str(error))

for result in st.session_state.get("tmdb_results", []):
    result_columns = st.columns([.7, 3.2, 1])
    if result.get("poster_path"):
        result_columns[0].image(f"{TMDB_IMAGE_URL}{result['poster_path']}", width=70)
    result_columns[1].markdown(
        f"**{result.get('title', 'Untitled')}**  \n{(result.get('release_date') or 'Year unknown')[:4]} · {result.get('vote_average', 0):.1f} / 10  \n{result.get('overview') or 'No overview available.'}"
    )
    if result_columns[2].button("Save", key=f"save_tmdb_{result['id']}"):
        try:
            details = get_movie_details(result["id"], tmdb_token)
            if add_tmdb_movie(to_movie_record(details)):
                st.success(f"{details.get('title', 'Movie')} was added to your collection.")
            else:
                st.info("That movie is already in your collection.")
            st.rerun()
        except TMDBError as error:
            st.error(str(error))

metric_columns = st.columns(3)
metric_columns[0].metric("Films in collection", len(movies))
metric_columns[1].metric("Average rating", f"{average_rating:.1f} / 10" if average_rating is not None else "—")
metric_columns[2].metric("Highest rated", f"{top_movie['rating']:.1f} / 10" if top_movie else "—")

st.markdown('<div class="section-label">Add to the shelf</div>', unsafe_allow_html=True)
with st.form("add_movie_form", clear_on_submit=True):
    form_columns = st.columns([2.4, 1.4, 1, 1.2, .8])
    movie_name = form_columns[0].text_input("Movie name")
    genre = form_columns[1].selectbox("Genre", ["Action", "Comedy", "Drama", "Thriller", "Science Fiction", "Other"])
    rating = form_columns[2].number_input("Rating", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    release_year = form_columns[3].number_input("Release year", min_value=1888, max_value=2100, value=2024, step=1)
    submitted = form_columns[4].form_submit_button("Add movie", type="primary")

if submitted:
    if not movie_name.strip():
        st.error("Enter a movie name before adding it.")
    else:
        add_movie(movie_name, genre, rating, release_year)
        st.success(f'“{movie_name.strip()}” was added to your shelf.')
        st.rerun()

left, right = st.columns([1.7, 1])
with left:
    st.markdown('<div class="section-label">Collection</div>', unsafe_allow_html=True)
    if movies:
        st.dataframe(
            movies,
            column_config={
                "movie_id": st.column_config.NumberColumn("ID", format="%d"),
                "movie_name": st.column_config.TextColumn("Movie"),
                "rating": st.column_config.NumberColumn("Rating", format="%.1f / 10"),
                "release_year": st.column_config.NumberColumn("Year", format="%d"),
            },
            column_order=["movie_name", "genre", "rating", "release_year"],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("Your shelf is empty. Add your first movie above.")

with right:
    st.markdown('<div class="section-label">Top pick</div>', unsafe_allow_html=True)
    if top_movie:
        st.markdown(
            f'<div class="spotlight"><small>Highest rated</small><h3>{top_movie["movie_name"]}</h3><p>{top_movie["genre"]} · {top_movie["release_year"]} · {top_movie["rating"]:.1f} / 10</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="spotlight"><small>Highest rated</small><h3>Nothing here yet</h3><p>Your best film is waiting to be added.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-label">Genre-wise summary</div>', unsafe_allow_html=True)
summary = get_genre_summary()
if summary:
    st.dataframe(summary, column_config={"genre": "Genre", "movie_count": "Films", "average_rating": st.column_config.NumberColumn("Average rating", format="%.2f / 10")}, hide_index=True, use_container_width=True)
else:
    st.caption("Genre statistics will appear once your collection has a movie.")