from urllib.parse import urlparse, urljoin
import requests, os, hashlib, json
from bs4 import BeautifulSoup

from paths import get_cache_dir

def extract_link_preview(url):
    cache_folder = get_cache_folder_for_url(url)
    preview_path = os.path.join(cache_folder, "preview.txt")

     # ✅ Check if cached preview exists
    if os.path.exists(preview_path):
        try:
            with open(preview_path, "r", encoding="utf-8") as f:
                print(f"Loaded from cache: {url}")
                return json.load(f)
        except Exception as e:
            print("Failed to load cached preview:", e)

    # 🛰️ Fetch preview from the web
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
    except Exception as e:
        print("Preview fetch failed:", e)
        return {"title": url, "description": "", "favicon": "", "thumbnail": ""}

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    description = ""
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()

    thumbnail = ""
    thumb_tag = soup.find("meta", attrs={"property": "og:image"})
    if thumb_tag and thumb_tag.get("content"):
        thumbnail = thumb_tag["content"].strip()

    favicon = ""
    icon_tag = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    if icon_tag and icon_tag.get("href"):
        icon_url = icon_tag["href"]
        if icon_url.startswith("//"):
            favicon = "https:" + icon_url
        elif icon_url.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(url)
            favicon = f"{parsed.scheme}://{parsed.netloc}{icon_url}"
        elif icon_url.startswith("http"):
            favicon = icon_url
        else:
            favicon = url + "/" + icon_url

    preview = {
        "title": title,
        "description": description,
        "favicon": favicon,
        "thumbnail": thumbnail
    }

    # 💾 Save preview to cache
    try:
        with open(preview_path, "w", encoding="utf-8") as f:
            json.dump(preview, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Failed to save preview cache:", e)

    return preview
    
def get_cache_folder_for_url(url):
    hashed = hashlib.md5(url.encode()).hexdigest()
    base_cache = get_cache_dir()  # like ~/.stashly/cache
    path = os.path.join(base_cache, hashed)
    os.makedirs(path, exist_ok=True)
    return path
