import time
from datetime import datetime
import json
from newspaper import Article, Config, build  # newspaper4k uses same imports

# List of sites (same as before, but now we use homepage URLs)
sites = [
    {"name": "Nyasa Times", "url": "https://www.nyasatimes.com/"},
    {"name": "Malawi 24", "url": "https://malawi24.com/"},
    {"name": "Face of Malawi", "url": "https://www.faceofmalawi.com/"},
    {"name": "Malawi Voice", "url": "https://www.malawivoice.com/"},
    {"name": "Maravi Express", "url": "https://www.maraviexpress.com/"},
    {"name": "Times 360 Malawi / Times Group", "url": "https://times.mw/"},
    {"name": "Nation Online (The Nation)", "url": "https://mwnation.com/"},
    {"name": "Malawi News Agency (MANA)", "url": "https://www.manaonline.gov.mw/"},
]

# Configuration (helps with parsing reliability)
config = Config()
config.memoize_articles = False  # Don't cache (we want fresh)
config.request_timeout = 10  # Seconds before timeout
config.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

all_news = []

for site in sites:
    print(f"Processing {site['name']}...")
    try:
        # Build the source → discovers article links from homepage
        paper = build(site["url"], config=config)

        # Limit to first N articles (most recent usually appear first)
        articles_to_process = paper.articles[:8]  # ← tune this number

        for article_obj in articles_to_process:
            try:
                article_obj.download()
                article_obj.parse()

                # Skip if no title or very short text
                if not article_obj.title or len(article_obj.text) < 100:
                    continue

                # Format date nicely (newspaper4k gives datetime object)
                pub_date = article_obj.publish_date
                if pub_date:
                    pub_str = pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")
                else:
                    pub_str = "N/A"

                all_news.append({
                    "title": article_obj.title.strip(),
                    "link": article_obj.url,
                    "published": pub_str,
                    "summary": article_obj.summary[:300] + "..." if article_obj.summary else article_obj.text[
                                                                                                 :300] + "...",
                    "text_preview": article_obj.text[:400] + "..." if article_obj.text else "",
                    "source": site["name"],
                    "authors": ", ".join(article_obj.authors) if article_obj.authors else "",
                    "top_image": article_obj.top_image if article_obj.top_image else ""
                })

                time.sleep(3)  # Be polite – delay between article downloads

            except Exception as e:
                print(f"  Failed to parse article {article_obj.url}: {e}")
                continue

        time.sleep(5)  # Extra delay between sites

    except Exception as e:
        print(f"Failed to build source {site['name']}: {e}")


# Sort by published date (newest first) – handle "N/A" gracefully
def parse_date(dt_str):
    if dt_str == "N/A":
        return datetime.min
    try:
        return datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S %z")
    except:
        return datetime.min


all_news.sort(key=lambda x: parse_date(x["published"]), reverse=True)

# Save to JSON
with open("malawi_news_newspaper4k.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)

print(f"Collected {len(all_news)} articles! Saved to malawi_news_newspaper4k.json")
