import sqlite3

from queries import QUERIES_CREATE_TABLES

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
