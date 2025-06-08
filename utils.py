from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def extract_link_preview(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else url

        # Description: Open Graph or meta description
        desc = ""
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc.get("content").strip()
        else:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                desc = meta_desc.get("content").strip()

        # Thumbnail from Open Graph
        thumbnail = ""
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            thumbnail = og_img.get("content").strip()

        # Favicon - try multiple rel types
        favicon = ""
        rel_candidates = ["icon", "shortcut icon", "apple-touch-icon", "apple-touch-icon-precomposed"]
        for rel in rel_candidates:
            icon_link = soup.find("link", rel=lambda x: x and rel in x.lower())
            if icon_link and icon_link.get("href"):
                raw_href = icon_link.get("href")
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                favicon = urljoin(base_url, raw_href).strip()
                if favicon:
                    break

        # Fallback: If no favicon found, try /favicon.ico
        if not favicon:
            parsed_url = urlparse(url)
            favicon = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"

        return {
            "title": title,
            "description": desc,
            "thumbnail": thumbnail,
            "favicon": favicon,
        }

    except Exception as e:
        print("Preview fetch failed:", e)
        return {
            "title": url,
            "description": "",
            "thumbnail": "",
            "favicon": "",
        }