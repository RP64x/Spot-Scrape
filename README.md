# Spotify Playlist Generator

A Python script that automatically builds a randomized Spotify playlist based on a set of search terms. It filters out low-quality and "ghost artist" tracks, so you end up with a playlist of real, popular artists only.

---

## How It Works

1. **Searches Spotify** for tracks using a list of search terms (e.g. "Bossa Nova", "Samba", "Brazilian")
2. **Filters by popularity** — removes tracks below a minimum popularity score
3. **Filters by artist** — removes artists with fewer than 10,000 followers or genres associated with background/ambient filler music
4. **Builds a playlist** — shuffles the remaining tracks, picks up to 50, and saves them to your Spotify account with a randomly generated name

---

## Example Output

```
Tracks found: 250
After popularity filter: 178
After ghost-artist filter: 94

50 tracks added to 'Randomized Playlist #k3!zb8@mx':
  Garota de Ipanema — João Gilberto (1,200,000 followers)
  Mas Que Nada — Sergio Mendes (980,000 followers)
  Aquarela do Brasil — Gal Costa (540,000 followers)
  ...
```

---

## Setup

### Step 1 — Install Python

Download and install Python from [python.org](https://www.python.org/downloads/). Version 3.9 or higher is recommended.

### Step 2 — Install the required libraries

Open a terminal (or PyCharm's built-in terminal) and run:

```
pip install spotipy python-dotenv
```

### Step 3 — Create a Spotify Developer app

1. Go to [developer.spotify.com](https://developer.spotify.com) and log in
2. Click **Create App**
3. Set the Redirect URI to `http://localhost:8000/callback`
4. Copy your **Client ID** and **Client Secret**

### Step 4 — Set up your credentials

1. Make a copy of `.env.example` and rename it to `.env`
2. Open `.env` and fill in your details:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_USERNAME=your_spotify_username_here
```

> ⚠️ Never share your `.env` file or upload it to GitHub — it contains your private credentials.

### Step 5 — Run the script

```
python main.py
```

A browser window will open asking you to log in to Spotify and grant permission. After that, the playlist will be created automatically.

---

## Customization

You can tweak the following values near the top of `main.py`:

| Variable | Default | Description |
|---|---|---|
| `SEARCH_TERMS` | Bossa Nova, Samba, etc. | Keywords used to find tracks |
| `MIN_ARTIST_FOLLOWERS` | 10,000 | Minimum followers an artist must have |
| `MIN_TRACK_POPULARITY` | 20 | Minimum Spotify popularity score (0–100) |
| `PLAYLIST_LIMIT` | 50 | Maximum number of tracks in the playlist |
