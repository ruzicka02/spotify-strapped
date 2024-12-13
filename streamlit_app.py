import streamlit as st

from db import db_connect
from queries import QUERY_FETCH_TOP_SONGS, QUERY_FETCH_TOP_ARTISTS, QUERY_FETCH_TOP_PLAYLISTS, QUERY_FETCH_ACTIVITY

def app_header():
    st.set_page_config(page_title="Spotify Strapped", page_icon="🎶")
    st.title("Spotify Strapped DEVEL")

def print_table(table: list[tuple[str]]):
    markdown = "Song | Artist | Played\n-|-|-\n" + "\n".join(["|".join([str(x) for x in row]) for row in table])
    st.markdown(markdown)

if __name__ == "__main__":
    app_header()
    tabs: list[st.delta_generator.DeltaGenerator] = st.tabs(["Songs", "Artists", "Playlists", "Activity"])

    conn, cur = db_connect()

    with tabs[0]:
        cur.execute(QUERY_FETCH_TOP_SONGS)
        names = cur.fetchall()

        print_table(names)

    with tabs[1]:
        cur.execute(QUERY_FETCH_TOP_ARTISTS)
        names = cur.fetchall()

        print_table(names)

    with tabs[2]:
        cur.execute(QUERY_FETCH_TOP_PLAYLISTS)
        names = cur.fetchall()

        print_table(names)

    with tabs[3]:
        cur.execute(QUERY_FETCH_ACTIVITY)
        names = cur.fetchall()

        print_table(names)
