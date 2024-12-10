import sys
import os
import json
import sqlite3

import spotipy
from dotenv import load_dotenv

load_dotenv()

def spotify_fetch(after: int | None = None) -> dict:
    sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
                        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
                        scope="user-read-recently-played"))

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
    cur.execute("""CREATE TABLE IF NOT EXISTS played (
        song_name TEXT,
        song_id TEXT,
        artist_name TEXT,
        artist_id TEXT,
        album_name TEXT,
        album_id TEXT,
        song_duration_ms INTEGER,
        played_at TEXT,
        playlist_uri TEXT
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cutoff (
        timestamp INTEGER
    );""")

def db_write_played(spotify_res: dict, cur: sqlite3.Cursor):
    for item in spotify_res['items']:
        track = item['track']
        context = item.get('context', {})

        song_name = track['name']
        song_id = track['id']
        artist_name = track['artists'][0]['name']
        artist_id = track['artists'][0]['id']
        album_name = track['album']['name']
        album_id = track['album']['id']
        song_duration_ms = track['duration_ms']
        played_at = item['played_at']
        playlist_uri = None

        if context and context.get("type") == "playlist":
            playlist_uri = context.get('uri', None)

        cur.execute("""
            INSERT INTO played (
                song_name, song_id, artist_name, artist_id, album_name, album_id,
                song_duration_ms, played_at, playlist_uri
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (song_name, song_id, artist_name, artist_id, album_name, album_id,
                song_duration_ms, played_at, playlist_uri))

def db_fetch_names(cur: sqlite3.Cursor) -> list[tuple]:
    cur.execute("SELECT song_name FROM played")

def db_fetch_play_count(cur: sqlite3.Cursor) -> list[tuple]:
    cur.execute("""
    SELECT
        song_name,
        artist_name,
        COUNT(*) AS play_count
    FROM
        played
    GROUP BY
        song_id, song_name
    ORDER BY
        play_count DESC
    LIMIT
        20;""")
    rows = cur.fetchall()

    return rows

def db_write_cutoff(cur: sqlite3.Cursor, cutoff: int):
    cur.execute("DELETE FROM cutoff")
    cur.execute("INSERT INTO cutoff (timestamp) VALUES (?);", (cutoff,))

def db_read_cutoff(cur: sqlite3.Cursor) -> int | None:
    cur.execute("SELECT timestamp FROM cutoff LIMIT 1")
    result = cur.fetchone()
    return result[0] if result else None

# ms since epoch -- time when the oldest song was played
# cutoff: int = int(results["cursors"]["before"])

if __name__ == "__main__":
    conn, cur = db_connect()
    db_init(cur)

    cutoff = db_read_cutoff(cur)
    results = spotify_fetch(cutoff)

    if results["items"]:

        if results.get("cursors", None):
            print(f"Saving cutoff timestamp {results["cursors"]["after"]}")
            db_write_cutoff(cur, int(results["cursors"]["after"]))

        db_write_played(results, cur)

        conn.commit()
        conn.close()
        # with open("results.json", "w") as f:
        #     f.write(json.dumps(results, indent=2, ensure_ascii=False))

        summary: list[str] = [str((x["track"]["name"], x["played_at"])) for x in results["items"]]

        print("\n".join(summary))

    cur.execute("SELECT COUNT(*) FROM played")
    print(f"Total records in DB: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(DISTINCT song_id) FROM played")
    print(f"Total unique songs in DB: {cur.fetchone()[0]}")

    names = db_fetch_play_count(cur)
    print("\n".join([f"{x[0]:50s}{x[1]:30s}{x[2]:4d}" for x in names]))


    if "-i" in sys.argv or "--interactive" in sys.argv:
        while True:
            print("Write SQL query, leave empty to end:")
            q = input()
            if not q:
                break

            try:
                cur.execute(q)
                if res := cur.fetchall():
                    print(res)
                conn.commit()
            except Exception as e:
                print(f"Oops! try again\n{e}")