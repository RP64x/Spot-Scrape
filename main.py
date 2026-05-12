import os
import random
from typing import Dict, List

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
USERNAME = os.getenv("SPOTIFY_USERNAME")

MIN_ARTIST_FOLLOWERS = 10_000
MIN_TRACK_POPULARITY = 20

BLOCKED_GENRES = {
    "background music", "relaxative", "focus beats", "study music",
    "sleep", "meditation", "nature sounds", "white noise", "lo-fi beats",
}

SEARCH_TERMS = [
    "Bossa Nova",
    "Samba",
    "Brazilian",
    "Brazil",
    "Brazilian Classical Guitar",
]

PLAYLIST_LIMIT = 50
REDIRECT_URI = "http://localhost:8000/callback"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def search_tracks(sp: spotipy.Spotify, terms: List[str]) -> List[dict]:
    """Search Spotify for tracks matching each term at a random offset."""
    tracks = []
    for term in terms:
        try:
            offset = random.randint(0, 950)
            results = sp.search(q=term, type="track", limit=50, offset=offset)
            tracks.extend(results["tracks"]["items"])
        except spotipy.exceptions.SpotifyException as e:
            print(f"Search failed for '{term}': {e}")
    return tracks


def fetch_artist_data(sp: spotipy.Spotify, artist_ids: List[str]) -> Dict[str, dict]:
    """Batch-fetch artist metadata keyed by artist ID."""
    artist_data = {}
    for i in range(0, len(artist_ids), 50):
        batch = sp.artists(artist_ids[i : i + 50])["artists"]
        for artist in batch:
            artist_data[artist["id"]] = {
                "followers": artist["followers"]["total"],
                "genres": {g.lower() for g in artist.get("genres", [])},
            }
    return artist_data


def is_ghost_artist(artist_id: str, artist_data: Dict[str, dict]) -> bool:
    """Return True if the artist should be excluded."""
    data = artist_data.get(artist_id)
    if not data:
        return True
    if data["followers"] < MIN_ARTIST_FOLLOWERS:
        return True
    if data["genres"] & BLOCKED_GENRES:
        return True
    return False


def generate_playlist_name() -> str:
    """Generate a randomized playlist name from letters, digits, and symbols."""
    letters = random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 5))
    digits = [str(d) for d in random.choices(range(10), k=random.randint(3, 5))]
    symbols = random.choices("!@#$%^&*()-_=+[]{}|\\:;,./?", k=random.randint(3, 5))
    parts = letters + digits + symbols
    random.shuffle(parts)
    return f"Randomized Playlist #{''.join(parts)}"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- Browse/search client (no user auth needed) ---
    browse_sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
    )

    # 1. Collect raw tracks
    raw_tracks = search_tracks(browse_sp, SEARCH_TERMS)
    print(f"Tracks found: {len(raw_tracks)}")

    # 2. Filter by track popularity
    popular_tracks = [t for t in raw_tracks if t["popularity"] >= MIN_TRACK_POPULARITY]
    print(f"After popularity filter: {len(popular_tracks)}")

    # 3. Fetch artist metadata
    artist_ids = list({t["artists"][0]["id"] for t in popular_tracks})
    artist_data = fetch_artist_data(browse_sp, artist_ids)

    # 4. Filter out ghost artists
    filtered_tracks = [
        t for t in popular_tracks
        if not is_ghost_artist(t["artists"][0]["id"], artist_data)
    ]
    print(f"After ghost-artist filter: {len(filtered_tracks)}")

    if not filtered_tracks:
        print("No tracks passed filtering. Consider lowering thresholds.")
        return

    if len(filtered_tracks) < PLAYLIST_LIMIT:
        print(f"Warning: only {len(filtered_tracks)} tracks available (target {PLAYLIST_LIMIT}).")

    # 5. Pick final tracks
    random.shuffle(filtered_tracks)
    final_tracks = filtered_tracks[:PLAYLIST_LIMIT]

    # --- Authenticated client ---
    auth_sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="playlist-modify-public",
            username=USERNAME,
        )
    )

    # 6. Create playlist and add tracks
    user_id = auth_sp.me()["id"]
    playlist_name = generate_playlist_name()
    playlist_description = (
        f"Randomized tracks · {MIN_ARTIST_FOLLOWERS:,}+ followers · "
        f"popularity {MIN_TRACK_POPULARITY}+ · ghost-artist filtered"
    )

    playlist = auth_sp.user_playlist_create(user_id, playlist_name, description=playlist_description)
    auth_sp.user_playlist_add_tracks(user_id, playlist["id"], [t["uri"] for t in final_tracks])

    # 7. Summary
    print(f"\n{len(final_tracks)} tracks added to '{playlist_name}':")
    for track in final_tracks:
        artist = track["artists"][0]
        followers = artist_data.get(artist["id"], {}).get("followers")
        follower_str = f"{followers:,} followers" if isinstance(followers, int) else "?"
        print(f"  {track['name']} — {artist['name']} ({follower_str})")


if __name__ == "__main__":
    main()
