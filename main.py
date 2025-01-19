import sys
import sqlite3
import time
from configparser import ConfigParser

from dotenv import dotenv_values

from queries import QUERY_FETCH_TOP_SONGS
from db import db_connect, db_init, db_read_cutoff, db_write_cutoff, db_write_played
from spotify import spotify_fetch


def single_user_fetch(cur: sqlite3.Cursor, env_values: dict, user: dict):
    cache_name = user.get("cache")
    if not cache_name:
        cache_name = ".cache"

    cutoff = db_read_cutoff(cur, user["user_id"])
    results = spotify_fetch(env_values, cutoff, "users/" + cache_name)

    print(f"=== {user.get('display_name')} ===")

    # non-zero amount of songs found
    if results["items"]:
        if results.get("cursors", None):
            print(f"Saving cutoff timestamp {results['cursors']['after']}")
            db_write_cutoff(cur, int(results["cursors"]["after"]), user["user_id"])

        db_write_played(results, cur, user["user_id"])

        # with open("results.json", "w") as f:
        #     f.write(json.dumps(results, indent=2, ensure_ascii=False))

        summary: list[str] = [
            str((x["track"]["name"], x["played_at"])) for x in results["items"]
        ]

        print("\n".join(summary), sep="\n")


def fetch_all_users(cur: sqlite3.Cursor, env_values: dict):
    config = ConfigParser()
    config.read("users/users.ini")

    for user in config:
        if user == "DEFAULT":
            continue

        single_user_fetch(cur, env_values, dict(config[user]) | {"user_id": user})


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
        # refresh-friendly representation of dotenv, unlike load_dotenv
        env_values = dotenv_values()
        refresh_period = int(env_values.get("REFRESH_PERIOD_S"))

        conn, cur = db_connect()
        db_init(cur)

        # fetch_all_users(cur, env_values)

        try:
            fetch_all_users(cur, env_values)
            # single_user_fetch(cur, env_values, {})
        except Exception as e:
            conn.close()
            print(type(e), e)

            print(
                f"Waking up at {time.asctime(time.gmtime(time.time() + refresh_period))} UTC"
            )
            time.sleep(refresh_period)
            continue

        conn.commit()

        if "-v" in sys.argv or "--verbose" in sys.argv:
            cur.execute("SELECT COUNT(*) FROM played")
            print(f"Total records in DB: {cur.fetchone()[0]}")

            cur.execute("SELECT COUNT(DISTINCT song_id) FROM played")
            print(f"Total unique songs in DB: {cur.fetchone()[0]}")

            cur.execute(QUERY_FETCH_TOP_SONGS + " LIMIT 20")
            names = cur.fetchall()
            print("\n".join([f"{x[0]:50s}{x[2]:30s}{x[4]:4d}" for x in names]))

        if "-i" in sys.argv or "--interactive" in sys.argv:
            interactive(conn, cur)

        conn.close()

        if "-O" in sys.argv or "--only-once" in sys.argv:
            break

        print(
            f"Waking up at {time.asctime(time.gmtime(time.time() + refresh_period))} UTC"
        )
        time.sleep(refresh_period)
