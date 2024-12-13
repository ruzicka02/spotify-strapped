import streamlit as st

from db import db_connect
from queries import QUERY_FETCH_TOP_SONGS, QUERY_FETCH_TOP_ARTISTS, QUERY_FETCH_TOP_PLAYLISTS, QUERY_FETCH_ACTIVITY

def app_header():
    st.set_page_config(page_title="Spotify Strapped", page_icon="🎶")
    st.title("Spotify Strapped DEVEL")

def print_table(table: list[tuple[str]], headers: list[str]):
    markdown = " | ".join(headers) + '\n'
    markdown += "|".join(['-' for _ in headers]) + '\n'
    markdown += "\n".join(["|".join([str(x) for x in row]) for row in table])
    st.markdown(markdown)

if __name__ == "__main__":
    app_header()
    tabs: list[st.delta_generator.DeltaGenerator] = st.tabs(["Songs", "Artists", "Playlists", "Activity"])

    conn, cur = db_connect()

    with tabs[0]:
        limit_songs = st.number_input("Limit", min_value=1, value=20, key="songs")

        cur.execute(QUERY_FETCH_TOP_SONGS + f" LIMIT {limit_songs}")
        names = cur.fetchall()

        print_table(names, ["Song", "Artist", "Played"])

    with tabs[1]:
        limit_artists = st.number_input("Limit", min_value=1, value=20, key="artists")

        cur.execute(QUERY_FETCH_TOP_ARTISTS + f" LIMIT {limit_artists}")
        names = cur.fetchall()

        print_table(names, ["Artist", "Played"])

    with tabs[2]:
        limit_playlists = st.number_input("Limit", min_value=1, value=10)

        cur.execute(QUERY_FETCH_TOP_PLAYLISTS + f" LIMIT {limit_playlists}")
        names = cur.fetchall()

        print_table(names, ["Playlist", "Played"])

    with tabs[3]:
        limit_activity = st.number_input("Limit", min_value=1, value=20)

        cur.execute(QUERY_FETCH_ACTIVITY + f" LIMIT {limit_activity}")
        names = cur.fetchall()

        print_table(names, ["Song", "Artist", "Timestamp"])
