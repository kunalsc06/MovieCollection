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
    :root { --ink: #171717; --muted: #6d6a64; --paper: #f3f0e9; --surface: #edf2ef; --white: #ffffff; --black: #111111; --gold: #c69a43; --line: #d7d2c8; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: var(--paper); }
    [data-testid="stAppViewContainer"] { background: transparent; }
    [data-testid="stHeader"] { background: rgba(243, 240, 233, .9); }
    [data-testid="stToolbar"] { right: 1rem; }
    label, .stMarkdown, p, span { color: var(--ink); }
    input, textarea, [data-baseweb="select"] > div { background: var(--white) !important; color: var(--ink) !important; border-color: #c9d4ce !important; border-radius: 0 !important; }
    input:focus, textarea:focus { border-color: var(--black) !important; box-shadow: 0 0 0 1px var(--black) !important; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    h1 { font-size: clamp(3.2rem, 8vw, 7.5rem); line-height: .88; margin: 0; max-width: 8ch; text-transform: uppercase; }
    h2 { font-size: 1.65rem; }
    .top-nav { align-items: center; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; padding: .8rem 0; }
    .brand { font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; font-weight: 700; letter-spacing: .04em; }
    .nav-links { color: var(--muted); font-size: .68rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .hero { border-bottom: 1px solid var(--line); display: grid; gap: 2rem; grid-template-columns: 1.4fr 1fr; padding: 4.5rem 0 4rem; }
    .eyebrow { color: var(--gold); font-size: .72rem; font-weight: 700; letter-spacing: .16em; margin-bottom: 1rem; text-transform: uppercase; }
    .hero-copy { align-self: end; color: var(--muted); font-family: Georgia, serif; font-size: 1.25rem; line-height: 1.35; max-width: 25rem; padding-bottom: .25rem; }
    .hero-copy strong { color: var(--ink); font-style: italic; }
    [data-testid="stMetric"] { background: var(--surface) !important; border: 1px solid #c9d4ce; border-radius: 0; opacity: 1 !important; padding: 1.15rem; }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: var(--black); font-family: 'Space Grotesk', sans-serif; font-size: 2rem; }
    .section-label { border-top: 1px solid var(--ink); color: var(--muted); font-size: .68rem; font-weight: 700; letter-spacing: .14em; margin: 3rem 0 .8rem; padding-top: .65rem; text-transform: uppercase; }
    .spotlight { background: var(--surface) !important; border: 1px solid #c9d4ce; border-radius: 0; color: var(--ink); opacity: 1 !important; padding: 1.35rem; min-height: 145px; }
    .spotlight small { color: var(--gold); font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    .spotlight h3, .spotlight h3 span { margin: .35rem 0; color: var(--ink) !important; }
    .spotlight p, .spotlight p span { color: var(--muted) !important; margin: 0; }
    .poster-marquee { height: 100vh; left: 0; opacity: .3; overflow: hidden; pointer-events: none; position: fixed; top: 0; width: 100%; z-index: 0; }
    .marquee-row { display: flex; gap: 1.4rem; height: 33vh; min-width: max-content; padding: 1.1rem 0; transform: translateX(-8%); }
    .marquee-row.row-one { animation: drift-left 75s linear infinite; }
    .marquee-row.row-two { animation: drift-right 90s linear infinite; transform: translateX(-42%); }
    .marquee-row.row-three { animation: drift-left 105s linear infinite; transform: translateX(-18%); }
    .marquee-poster { background: #d7d2c8; flex: 0 0 18rem; height: 30vh; overflow: hidden; }
    .marquee-poster img { filter: grayscale(1) sepia(.18) contrast(.82); height: 100%; object-fit: cover; width: 100%; }
    .marquee-shade { background: linear-gradient(90deg, var(--paper) 0%, transparent 16%, transparent 84%, var(--paper) 100%), linear-gradient(180deg, var(--paper) 0%, transparent 24%, transparent 70%, var(--paper) 100%); inset: 0; position: absolute; }
    .main .block-container { position: relative; z-index: 1; }
    @keyframes drift-left { from { transform: translateX(-8%); } to { transform: translateX(-48%); } }
    @keyframes drift-right { from { transform: translateX(-42%); } to { transform: translateX(-2%); } }
    @media (prefers-reduced-motion: reduce) { .marquee-row { animation: none !important; } }
    .stButton > button, .stButton > button span, [data-testid="stFormSubmitButton"] > button, [data-testid="stFormSubmitButton"] > button span { background: var(--surface) !important; color: var(--ink) !important; border: 1px solid #c9d4ce; border-radius: 0; font-weight: 700; opacity: 1 !important; transition: background .2s ease, color .2s ease, transform .2s ease; }
    .stButton > button:hover, .stButton > button:hover span, [data-testid="stFormSubmitButton"] > button:hover, [data-testid="stFormSubmitButton"] > button:hover span { background: var(--gold) !important; border-color: var(--gold); color: var(--black) !important; transform: translateY(-1px); }
    .stButton > button:focus, [data-testid="stFormSubmitButton"] > button:focus { box-shadow: 0 0 0 2px var(--paper), 0 0 0 4px var(--gold); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 0; overflow: hidden; }
    [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stAlert"], [data-testid="stToast"], [role="alert"] { background: var(--surface) !important; border: 1px solid #c9d4ce; border-radius: 0; opacity: 1 !important; padding: 1rem; }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"], [data-testid="stForm"] [data-testid="column"] { background: var(--surface) !important; opacity: 1 !important; }
    @media (max-width: 700px) { .hero { grid-template-columns: 1fr; padding: 3rem 0; } h1 { font-size: 4rem; } .nav-links { display: none; } }
    </style>
    """,
    unsafe_allow_html=True,
)

marquee_posters = [
    ("The Matrix", "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"),
    ("The Incredibles", "/2LqaLgk4Z226KkgPJuiOQ58b9g.jpg"),
    ("Pulp Fiction", "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"),
    ("The Godfather", "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"),
    ("Spirited Away", "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg"),
    ("Interstellar", "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"),
    ("Parasite", "/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"),
    ("Moonlight", "/4911T5FbJ9eD2Faz5Z8s8M7n7nE.jpg"),
]
poster_tiles = "".join(
    f'<div class="marquee-poster"><img src="https://image.tmdb.org/t/p/w342{path}" alt="{title} poster"></div>'
    for title, path in marquee_posters
)
st.markdown(
    f'<div class="poster-marquee" aria-hidden="true"><div class="marquee-row row-one">{poster_tiles}{poster_tiles}</div><div class="marquee-row row-two">{poster_tiles}{poster_tiles}</div><div class="marquee-row row-three">{poster_tiles}{poster_tiles}</div><div class="marquee-shade"></div></div>',
    unsafe_allow_html=True,
)

initialize_database()
movies = get_movies()
average_rating = get_average_rating()
top_movie = get_highest_rated_movie()

st.markdown(
    '<div class="top-nav"><div class="brand">REEL / SHELF</div><div class="nav-links">COLLECTION &nbsp;&nbsp; DISCOVER &nbsp;&nbsp; INSIGHTS</div></div><div class="hero"><div><div class="eyebrow">Personal film archive / 2026</div><h1>Reel<br>Shelf</h1></div><div class="hero-copy">A considered home for the films that stay with you. <strong>Search, save, and see your taste take shape.</strong></div></div>',
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
    with st.container(border=True):
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