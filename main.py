import sys
import os
import sqlite3

import spotipy
from dotenv import load_dotenv

from queries import QUERIES_CREATE_TABLES, QUERY_FETCH_PLAY_COUNT
from streamlit_app import app_header, print_table

load_dotenv()


def spotify_fetch(after: int | None = None) -> dict:
    sp = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
            scope="user-read-recently-played",
        )
    )

    # 50 most recent songs
    # spotify allows time limits, (before=..., after=...)
    # but we can never get more than 50 most recent
    after = after if after and after > 0 else None
    results = sp.current_user_recently_played(after=after)

    print(len(results.get("items", [])), "items fetched from Spotify")

    return results


def db_connect(name: str = "data.db") -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    return conn, cur


def db_init(cur: sqlite3.Cursor):
    for q in QUERIES_CREATE_TABLES:
        cur.execute(q)


def db_write_played(spotify_res: dict, cur: sqlite3.Cursor):
    for item in spotify_res["items"]:
        track = item["track"]
        context = item.get("context", {})

        song_name = track["name"]
        song_id = track["id"]
        artist_name = track["artists"][0]["name"]
        artist_id = track["artists"][0]["id"]
        album_name = track["album"]["name"]
        album_id = track["album"]["id"]
        song_duration_ms = track["duration_ms"]
        played_at = item["played_at"]
        playlist_uri = None

        if context and context.get("type") == "playlist":
            playlist_uri = context.get("uri", None)

        cur.execute(
            """
            INSERT INTO played (
                song_name, song_id, artist_name, artist_id, album_name, album_id,
                song_duration_ms, played_at, playlist_uri
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            (
                song_name,
                song_id,
                artist_name,
                artist_id,
                album_name,
                album_id,
                song_duration_ms,
                played_at,
                playlist_uri,
            ),
        )


def db_write_cutoff(cur: sqlite3.Cursor, cutoff: int):
    cur.execute("DELETE FROM cutoff")
    cur.execute("INSERT INTO cutoff (timestamp) VALUES (?);", (cutoff,))


def db_read_cutoff(cur: sqlite3.Cursor) -> int | None:
    cur.execute("SELECT timestamp FROM cutoff LIMIT 1")
    result = cur.fetchone()
    return result[0] if result else None


def single_fetch(cur: sqlite3.Cursor):
    cutoff = db_read_cutoff(cur)
    results = spotify_fetch(cutoff)

    # non-zero amount of songs found
    if results["items"]:
        if results.get("cursors", None):
            print(f"Saving cutoff timestamp {results["cursors"]["after"]}")
            db_write_cutoff(cur, int(results["cursors"]["after"]))

        db_write_played(results, cur)

        # with open("results.json", "w") as f:
        #     f.write(json.dumps(results, indent=2, ensure_ascii=False))

        summary: list[str] = [
            str((x["track"]["name"], x["played_at"])) for x in results["items"]
        ]

        print("\n".join(summary))


def interactive(conn: sqlite3.Connection, cur: sqlite3.Cursor):
    while True:
        print("Write SQL query, leave empty to end:")
        q = input()
        if not q:
            return

        try:
            cur.execute(q)
            if res := cur.fetchall():
                print(res)
            conn.commit()
        except Exception as e:
            print(f"Oops! try again\n{e}")



if __name__ == "__main__":
    conn, cur = db_connect()
    db_init(cur)

    single_fetch(cur)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM played")
    print(f"Total records in DB: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(DISTINCT song_id) FROM played")
    print(f"Total unique songs in DB: {cur.fetchone()[0]}")

    cur.execute(QUERY_FETCH_PLAY_COUNT)
    names = cur.fetchall()
    print("\n".join([f"{x[0]:50s}{x[1]:30s}{x[2]:4d}" for x in names]))

    if "-i" in sys.argv or "--interactive" in sys.argv:
        interactive(conn, cur)

    if "--no-streamlit" not in sys.argv:
        app_header()
        print_table(names)

    conn.close()