# Malawi News Aggregator

A simple yet powerful Python-based news aggregator focused on **Malawian sources**. It collects the latest headlines, summaries, and (optionally) full article content from major Malawi news outlets like Nyasa Times, Malawi 24, Nation Online, and more.

Two modes are supported:
- **Lightweight RSS mode** → fast, polite, reliable headlines via public feeds.
- **Full scraping mode** → richer data (cleaned text, images, better dates) using Newspaper4k.

Built for personal/educational use in Blantyre, Malawi — great for staying updated on local politics, economy, markets (like Wakawaka), and national news.

Includes a **single-page HTML dashboard** that loads the generated JSON and displays articles as beautiful, responsive cards.

## Features

- Collects from 8+ popular Malawi news sites
- RSS parsing (fast & stable) or Newspaper4k scraping (detailed extraction)
- Sorts articles by publish date (newest first)
- Outputs clean JSON for easy reuse
- Simple, modern single-file HTML frontend (no backend/server needed)
- Polite scraping: delays, user-agent, error handling
- Requirements frozen in `requirements.txt`

## Demo Screenshots

(Add screenshots here later – e.g. terminal output, JSON file, and the HTML page in browser)

Example card on the website:
- **Title**: ANALYSIS | Ben Phiri’s hands-on leadership finally breaks the Wakawaka deadlock
- **Source**: Nyasa Times • Feb 4, 2026
- **Summary**: For more than four years, the Wakawaka market saga has stood as a symbol of policy paralysis...
- **Read more** → link to original
- (Optional image from article if available)

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR-USERNAME/malawi-news-aggregator.git
   cd malawi-news-aggregator
