import streamlit as st

from db import db_connect
from queries import QUERY_FETCH_PLAY_COUNT

def app_header():
    st.set_page_config(page_title="Spotify Strapped", page_icon="🎶")
    st.title("Spotify Strapped DEVEL")

def print_table(table: list[tuple[str]]):
    markdown = "Song | Artist | Played\n-|-|-\n" + "\n".join(["|".join([str(x) for x in row]) for row in table])
    st.markdown(markdown)

if __name__ == "__main__":
    app_header()

    conn, cur = db_connect()
    cur.execute(QUERY_FETCH_PLAY_COUNT)
    names = cur.fetchall()

    print_table(names)