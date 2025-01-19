import urllib

import spotipy
import bs4

def spotify_fetch(env_values: dict, after: int | None = None, cache_path: str = "users/.cache") -> dict:
    sp = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyOAuth(
            client_id=env_values.get("SPOTIFY_CLIENT_ID"),
            client_secret=env_values.get("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=env_values.get("SPOTIFY_REDIRECT_URI"),
            scope="user-read-recently-played",
            show_dialog=True,
            cache_handler=spotipy.CacheFileHandler(cache_path=cache_path),
        )
    )

    # 50 most recent songs
    # spotify allows time limits, (before=..., after=...)
    # but we can never get more than 50 most recent
    after = after if after and after > 0 else None
    results = sp.current_user_recently_played(after=after)

    print(len(results.get("items", [])), "items fetched from Spotify")

    return results


def public_playlist_name(playlist_id: str) -> str | None:
    """
    Spotify has a nice API endpoint, https://developer.spotify.com/documentation/web-api/reference/get-playlist
    This does not work for Spotify-created playlists
    Workaround was earlier possible with https://developer.spotify.com/documentation/web-api/reference/get-a-categories-playlists
    This feature got discontinued in Nov 2024, so we just get the name from the webpage
    """
    try:
        res = urllib.request.urlopen(f"https://open.spotify.com/playlist/{playlist_id}").read()
    except urllib.error.HTTPError:
        return None

    # alternatively bs.title.name, but this contains extra junk
    bs_res = bs4.BeautifulSoup(res, "html.parser").head.find("meta", attrs={"property": "og:title"})
    return bs_res.get("content") if bs_res else None