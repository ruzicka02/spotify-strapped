import os
import json

import spotipy
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
                    client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                    client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                    redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
                    scope="user-read-recently-played"))

# 50 most recent songs
# spotify allows time limits, (before=..., after=...)
# but we can never get more than 50 most recent
results = sp.current_user_recently_played()

with open("results.json", "w") as f:
    f.write(json.dumps(results, indent=2, ensure_ascii=False))

summary: list[str] = [str((x["track"]["name"], x["played_at"])) for x in results["items"]]

print("\n".join(summary))