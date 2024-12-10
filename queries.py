QUERIES_CREATE_TABLES: list[str] = [
    """CREATE TABLE IF NOT EXISTS played (
        song_name TEXT,
        song_id TEXT,
        artist_name TEXT,
        artist_id TEXT,
        album_name TEXT,
        album_id TEXT,
        song_duration_ms INTEGER,
        played_at TEXT,
        playlist_uri TEXT
    );""",
    """CREATE TABLE IF NOT EXISTS cutoff (
        timestamp INTEGER
    );""",
]

QUERY_FETCH_PLAY_COUNT: str = """
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
        20;"""


QUERY_FETCH_ACTIVITY = """
    SELECT
        song_name,
        artist_name,
        played_at
    FROM
        played;"""
