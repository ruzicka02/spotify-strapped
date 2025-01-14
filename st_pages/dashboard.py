import time
from configparser import ConfigParser

import streamlit as st

from db import db_connect, db_read_cutoff
from queries import QUERY_FETCH_TOP_SONGS, QUERY_FETCH_TOP_ARTISTS, QUERY_FETCH_TOP_PLAYLISTS, QUERY_FETCH_ACTIVITY

ARTIST_BASE_URL = "https://open.spotify.com/artist"
SONG_BASE_URL = "https://open.spotify.com/track"
PLAYLIST_BASE_URL = "https://open.spotify.com/playlist"

def app_header():
    st.set_page_config(page_title="Spotify Strapped", page_icon="🎶")
    st.title("Spotify Strapped DEVEL")

def user_selector():
    config = ConfigParser()
    config.read("users/users.ini")
    user_list = list(config)
    user_list.remove("DEFAULT")

    return user_list

def preprocess_table_urls(table: list[tuple[str]], urls: dict[int, tuple[str, int]]) -> list[tuple[str]]:
    """
    urls: idx of text field -> base url + idx of uri
    """
    new_table = []
    for row in table:
        row = list([(x if x is not None else "???") for x in row])
        for k, v in urls.items():
            # in some cases (playlists), the DB content is actually URI
            # as ID is base 64, it cannot contain ':', so splitting by it SHOULD be safe
            spotify_id = row[v[1]].split(':')[-1]

            # create a Markdown URL, row[k] stays as the visible text
            # URL is "Base URL/Spotify ID"
            row[k] = f"[{row[k]}]({v[0]}/{spotify_id})"
            row[v[1]] = None
        new_table.append([x for x in row if x])

    return new_table

def print_table(table: list[tuple[str]], headers: list[str]):
    markdown = " | ".join(headers) + '\n'
    markdown += "|".join(['-' for _ in headers]) + '\n'
    markdown += "\n".join(["|".join([str(x) for x in row]) for row in table])
    st.markdown(markdown)

app_header()
username = st.selectbox("Username", user_selector())


conn, cur = db_connect()

cutoff: int = db_read_cutoff(cur, username)
st.markdown(f"Last cutoff time: **{time.asctime(time.gmtime(cutoff / 1000))} GMT**")

tabs: list[st.delta_generator.DeltaGenerator] = st.tabs(["Songs", "Artists", "Playlists", "Activity"])

with tabs[0]:
    limit_songs = st.number_input("Limit", min_value=1, value=20, key="songs")

    cur.execute(QUERY_FETCH_TOP_SONGS.format(username) + f" LIMIT {limit_songs}")
    names = cur.fetchall()

    names = preprocess_table_urls(names, {0: (SONG_BASE_URL, 1),
                                            2: (ARTIST_BASE_URL, 3)})
    print_table(names, ["Song", "Artist", "Played", "Total time (s)"])

with tabs[1]:
    limit_artists = st.number_input("Limit", min_value=1, value=20, key="artists")

    cur.execute(QUERY_FETCH_TOP_ARTISTS.format(username) + f" LIMIT {limit_artists}")
    names = cur.fetchall()

    names = preprocess_table_urls(names, {0: (ARTIST_BASE_URL, 1)})
    print_table(names, ["Artist", "Played", "Total time (s)"])

with tabs[2]:
    limit_playlists = st.number_input("Limit", min_value=1, value=10)

    cur.execute(QUERY_FETCH_TOP_PLAYLISTS.format(username) + f" LIMIT {limit_playlists}")
    names = cur.fetchall()

    # TODO... fetch real playlist names from Spotify API
    names = preprocess_table_urls(names, {0: (PLAYLIST_BASE_URL, 1)})
    print_table(names, ["Playlist", "Played", "Total time (s)"])

with tabs[3]:
    limit_activity = st.number_input("Limit", min_value=1, value=20)

    cur.execute(QUERY_FETCH_ACTIVITY.format(username) + f" LIMIT {limit_activity}")
    names = cur.fetchall()

    names = preprocess_table_urls(names, {0: (SONG_BASE_URL, 1),
                                            2: (ARTIST_BASE_URL, 3)})
    print_table(names, ["Song", "Artist", "Timestamp"])
