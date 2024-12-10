import sys
import os
import sqlite3
import time

import spotipy
from dotenv import load_dotenv

from queries import QUERY_FETCH_PLAY_COUNT
from db import db_connect, db_init, db_read_cutoff, db_write_cutoff, db_write_played


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
    while True:
        load_dotenv()

        refresh_period = int(os.environ.get("REFRESH_PERIOD_S"))

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

        conn.close()

        if "-O" in sys.argv or "--only-once" in sys.argv:
            break

        print(f"Waking up at {time.asctime(time.gmtime(time.time() + refresh_period))} UTC")
        time.sleep(refresh_period)

