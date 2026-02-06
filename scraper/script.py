import time
import json
import hashlib
from newspaper import Article, Config, build
from datetime import datetime, timezone
from pathlib import Path
import feedparser

SITES = [
    {
        "name": "Nyasa Times",
        "url": "https://www.nyasatimes.com/",
        "rss": ["https://www.nyasatimes.com/feed/"]
    },
    {
        "name": "Malawi 24",
        "url": "https://malawi24.com/",
        "rss": ["https://malawi24.com/feed/"]
    },
    {
        "name": "Face of Malawi",
        "url": "https://www.faceofmalawi.com/",
        "rss": ["https://www.faceofmalawi.com/feed/"]
    },
    {
        "name": "Malawi Voice",
        "url": "https://www.malawivoice.com/",
        "rss": ["https://www.malawivoice.com/feed/"]
    },
    {
        "name": "Maravi Express",
        "url": "https://www.maraviexpress.com/",
        "rss": ["https://www.maraviexpress.com/feed/"]
    },
    {
        "name": "Times 360 Malawi / Times Group",
        "url": "https://times.mw/",
        "rss": ["https://times.mw/feed/"]
    },
    {
        "name": "Nation Online (The Nation)",
        "url": "https://mwnation.com/",
        "rss": ["https://mwnation.com/feed/"]
    },
    {
        "name": "Malawi News Agency (MANA)",
        "url": "https://www.manaonline.gov.mw/",
        "rss": []
    },
    {"name": "Maravi Post", "url": "https://www.maravipost.com/"},
    {"name": "Zodiak Malawi", "url": "https://zodiakmalawi.com/"},
    {"name": "Capital FM Malawi", "url": "https://www.capitalfm.mw/"},
    {"name": "Focus Malawi", "url": "https://www.focusmalawi.com/"},
    {"name": "Biz Malawi", "url": "https://www.bizmalawi.com/"},
    {"name": "Business Malawi", "url": "https://businessmalawi.com/"},
    {"name": "The Daily Times / Times Group", "url": "https://times.mw/"},
    {"name": "The Nation Malawi", "url": "https://mwnation.com/"},
]

CONFIG = Config()
CONFIG.memoize_articles = False
CONFIG.request_timeout = 12
CONFIG.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

MAX_PER_SOURCE = 10
REQUEST_DELAY = 1.5

def safe_parse_date(entry):
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    except:
        pass
    return None

def normalize_date(dt):
    if not dt:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    if not dt.tzinfo:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def article_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def extract_article(url, source_name):
    try:
        art = Article(url, config=CONFIG)
        art.download()
        art.parse()

        if not art.title or len(art.text) < 120:
            return None

        pub = normalize_date(art.publish_date)

        return {
            "title": art.title.strip(),
            "link": url,
            "published": pub.strftime("%a, %d %b %Y %H:%M:%S %z"),
            "timestamp": int(pub.timestamp()),
            "summary": (art.summary[:300] + "...") if art.summary else art.text[:300] + "...",
            "text_preview": art.text[:400] + "...",
            "source": source_name,
            "authors": ", ".join(art.authors) if art.authors else "",
            "top_image": art.top_image or "",
        }

    except:
        return None

def collect_from_rss(site):
    collected = []
    seen = set()

    for rss_url in site["rss"]:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:MAX_PER_SOURCE * 2]:
            url = entry.link
            h = article_hash(url)

            if h in seen:
                continue

            seen.add(h)

            article_data = extract_article(url, site["name"])
            if article_data:
                collected.append(article_data)

            if len(collected) >= MAX_PER_SOURCE:
                break

            time.sleep(REQUEST_DELAY)

    return collected

def collect_from_homepage(site):
    collected = []
    seen = set()

    try:
        paper = build(site["url"], config=CONFIG)

        for art_obj in paper.articles[:MAX_PER_SOURCE * 3]:
            url = art_obj.url
            h = article_hash(url)

            if h in seen:
                continue

            seen.add(h)

            article_data = extract_article(url, site["name"])
            if article_data:
                collected.append(article_data)

            if len(collected) >= MAX_PER_SOURCE:
                break

            time.sleep(REQUEST_DELAY)

    except:
        pass

    return collected

all_news = []

for site in SITES:
    print(f"Processing {site['name']}")


    site.setdefault("rss", [])

    site_articles = []

    if site.get("rss"):
        site_articles = collect_from_rss(site)

    if len(site_articles) < MAX_PER_SOURCE:
        site_articles.extend(collect_from_homepage(site))

    all_news.extend(site_articles[:MAX_PER_SOURCE])

    time.sleep(2)


all_news.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

for item in all_news:
    item.pop("timestamp", None)

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR.parent / "public"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

OUT = PUBLIC_DIR / "malawi_news.json"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"Collected {len(all_news)} articles → {OUT}")
