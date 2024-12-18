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
    )""",
    """CREATE TABLE IF NOT EXISTS cutoff (
        timestamp INTEGER
    )""",
]

QUERY_FETCH_TOP_SONGS: str = """
    SELECT
        song_name,
        song_id,
        artist_name,
        artist_id,
        COUNT(*) AS play_count,
        SUM(song_duration_ms) / 1000 AS total_time
    FROM
        played
    GROUP BY
        song_id
    ORDER BY
        play_count DESC, song_duration_ms DESC"""
# TODO... choose what to order by (play_count/total_time)

QUERY_FETCH_TOP_ARTISTS: str = """
    SELECT
        artist_name,
        artist_id,
        COUNT(*) AS play_count,
        SUM(song_duration_ms) / 1000 AS total_time
    FROM
        played
    GROUP BY
        artist_id
    ORDER BY
        play_count DESC, total_time DESC"""

QUERY_FETCH_TOP_PLAYLISTS: str = """
    SELECT
        playlist_uri,
        playlist_uri,
        COUNT(*) AS play_count,
        SUM(song_duration_ms) / 1000 AS total_time
    FROM
        played
    GROUP BY
        playlist_uri
    ORDER BY
        play_count DESC, total_time DESC"""


QUERY_FETCH_ACTIVITY = """
    SELECT
        song_name,
        song_id,
        artist_name,
        artist_id,
        played_at
    FROM
        played
    ORDER BY
        played_at DESC"""
