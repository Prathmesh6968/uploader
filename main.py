import requests
import os
import re
from tqdm import tqdm
from internetarchive import upload

# ================= SUPABASE CONFIG =================
SUPABASE_URL = "https://jkszncegihkumudtbawr.supabase.co"
SUPABASE_KEY = "sb_publishable_5u5hvA8zL0nxdJRPvvKhIA_-YvXylqG"

DB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ================= ARCHIVE.ORG CONFIG =================
ARCHIVE_ACCESS_KEY = "UhSUlvL3XXWjlUPT"
ARCHIVE_SECRET_KEY = "iIpzUEk2FTPbgiba"

# ================= HELPERS =================
def safe_name(text):
    return re.sub(r'[\\/:*?"<>|]', '', text)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def download_video(url, filename):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print("❌ Download failed")
        return False

    total = int(r.headers.get("content-length", 0))
    with open(filename, "wb") as f, tqdm(
        total=total, unit="B", unit_scale=True, desc="Downloading"
    ) as bar:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    return True

# ================= MAL (SAME AS OLD SCRAPER) =================
def get_or_create_anime(mal_url, anime_name):
    slug = slugify(anime_name)

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/anime_data?on_conflict=slug",
        headers={**DB_HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"},
        json={
            "title": anime_name,
            "slug": slug,
            "mal_url": mal_url
        }
    )

    if r.status_code not in (200, 201):
        print("❌ Anime insert error:", r.text)
        raise SystemExit

    return r.json()[0]["id"]

# ================= EPISODE CHECK =================
def episode_exists(anime_id, season, episode):
    url = (
        f"{SUPABASE_URL}/rest/v1/episodes_data"
        f"?anime_id=eq.{anime_id}&season=eq.{season}&episode=eq.{episode}"
        f"&select=id"
    )

    r = requests.get(url, headers=DB_HEADERS)
    if r.status_code != 200:
        return False

    return len(r.json()) > 0

# ================= EPISODE SAVE (UNCHANGED) =================
def save_episode(anime_id, season, episode, video_url, source_url):
    payload = {
        "anime_id": anime_id,
        "season": season,
        "episode": episode,
        "iframe": video_url,   # 🔥 SAME FIELD NAME
        "url": source_url
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/episodes_data",
        headers=DB_HEADERS,
        json=payload
    )

    if r.status_code not in (200, 201):
        print("❌ Episode insert error:", r.text)
    else:
        print(f"✅ DB saved S{season}E{episode}")

# ================= MAIN =================
print("=== ARCHIVE AUTO PIPELINE (AUTO-SKIP ENABLED) ===\n")

mal_url = input("MyAnimeList URL: ").strip()
anime_name = safe_name(input("Anime Name: ").strip())
season = int(input("Season number: "))
episode = int(input("Starting Episode number: "))
quality = input("Quality (480p / 720p / 1080p): ").strip()

anime_id = get_or_create_anime(mal_url, anime_name)

while True:
    # 🔥 AUTO-SKIP EXISTING EPISODES
    if episode_exists(anime_id, season, episode):
        print(f"⏭️ S{season}E{episode} already exists — skipping")
        episode += 1
        continue

    download_url = input(
        f"\nDownload link for Episode {episode} (blank / q to stop): "
    ).strip()

    if not download_url or download_url.lower() == "q":
        print("🛑 Stopped by user")
        break

    filename = f"[AnimeStreamAll] {anime_name} S{season:02d}E{episode:02d} {quality}.mp4"

    print("⬇ Downloading...")
    if not download_video(download_url, filename):
        break

    identifier = f"{slugify(anime_name)}-s{season}e{episode}-{quality}"

    print("⬆ Uploading to Archive.org...")
    upload(
        identifier,
        files={filename: filename},
        metadata={
            "title": f"{anime_name} S{season}E{episode}",
            "mediatype": "movies"
        },
        access_key=ARCHIVE_ACCESS_KEY,
        secret_key=ARCHIVE_SECRET_KEY
    )

    video_url = f"https://archive.org/download/{identifier}/{filename}"

    save_episode(anime_id, season, episode, video_url, download_url)

    episode += 1  # 🔥 NEXT EPISODE AUTO

print("\n🎉 ALL DONE")
