import sqlite3

from queries import QUERIES_CREATE_TABLES

def db_connect(name: str = "data.db") -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    return conn, cur


def db_init(cur: sqlite3.Cursor):
    for q in QUERIES_CREATE_TABLES:
        cur.execute(q)


def db_write_played(spotify_res: dict, cur: sqlite3.Cursor, user_id: str):
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
                song_duration_ms, played_at, playlist_uri, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
                user_id,
            ),
        )


def db_write_cutoff(cur: sqlite3.Cursor, cutoff: int, user_id: str):
    cur.execute(f"DELETE FROM cutoff WHERE user_id = '{user_id}'")
    cur.execute("INSERT INTO cutoff (timestamp, user_id) VALUES (?, ?);", (cutoff, user_id))


def db_read_cutoff(cur: sqlite3.Cursor, user_id: str) -> int | None:
    cur.execute(f"SELECT timestamp FROM cutoff WHERE user_id = '{user_id}' LIMIT 1")
    result = cur.fetchone()
    return result[0] if result else None


def db_write_playlist(cur: sqlite3.Cursor, id: str, name: str):
    cur.execute("INSERT INTO playlist_names (id, name) VALUES (?, ?);", (id, name))


def db_get_playlist_name(cur: sqlite3.Cursor, identifier: str) -> str | None:
    # check in case URI was given instead of ID stored in DB
    if ':' in identifier:
        identifier = identifier.split(':')[-1]

    cur.execute("SELECT name FROM playlist_names WHERE id = ? LIMIT 1", (identifier,))
    result = cur.fetchone()
    return result[0] if result else None