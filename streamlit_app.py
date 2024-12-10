import streamlit as st

def app_header():
    st.set_page_config(page_title="Spotify Strapped", page_icon="🎶")
    st.title("Spotify Strapped DEVEL")

def print_table(table: list[tuple[str]]):
    markdown = "Song | Artist | Played\n-|-|-\n" + "\n".join(["|".join([str(x) for x in row]) for row in table])
    st.markdown(markdown)