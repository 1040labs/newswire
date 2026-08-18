from flask import Flask, render_template
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def fetch_bbc_news():
    """Fetch news articles from BBC News RSS feed."""
    feed = feedparser.parse("https://feeds.bbci.co.uk/news/rss.xml")
    articles = []
    for entry in feed.entries[:10]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "source": "BBC News"
        })
    return articles

def scrape_hacker_news():
    """Scrape top stories from Hacker News."""
    response = requests.get("https://news.ycombinator.com")
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for item in soup.select(".titleline > a")[:10]:
        articles.append({
            "title": item.get_text(),
            "link": item.get("href", ""),
            "published": "",
            "source": "Hacker News"
        })
    return articles

def fetch_whitehouse_news():
    """Scrape top stories directly from the official White House News HTML page."""
    url = "https://www.whitehouse.gov/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = []
            items = soup.select(".news-item__title a")
            
            if not items:
                items = soup.select("article h2 a") or soup.select("article h3 a")
                
            if not items:
                items = [a for a in soup.find_all("a", href=True) if "/briefing-room/" in a["href"] or "/releases/" in a["href"]]

            for item in items[:10]:
                title = item.get_text(strip=True)
                link = item.get("href", "")
                
                if link and not link.startswith("http"):
                    link = f"https://www.whitehouse.gov{link}"
                
                if title and link and not any(a["link"] == link for a in articles):
                    articles.append({
                        "title": title,
                        "link": link,
                        "published": "",
                        "source": "White House"
                    })
            return articles
        else:
            print(f"White House scrape failed with status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error scraping White House: {e}")
        return []

def fetch_oann_news():
    """Fetch top stories from One America News Network RSS feed."""
    feed_url = "https://www.oann.com/feed/"
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:10]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "source": "OANN"
        })
    return articles

def fetch_kernel_news():
    """Fetch latest Linux kernel releases from Kernel.org."""
    feed_url = "https://www.kernel.org/feeds/kdist.xml"
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:10]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "source": "Kernel.org"
        })
    return articles

def fetch_9to5linux_news():
    """Fetch top stories from 9to5Linux."""
    feed_url = "https://9to5linux.com/feed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "source": "9to5Linux"
                })
            return articles
        else:
            print(f"9to5Linux feed failed with status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching 9to5Linux: {e}")
        return []

@app.route("/")
def index():
    # Fetch news from all 6 incredible sources!
    bbc_articles = fetch_bbc_news()
    hn_articles = scrape_hacker_news()
    wh_articles = fetch_whitehouse_news()
    oann_articles = fetch_oann_news()
    kernel_articles = fetch_kernel_news()
    linux_articles = fetch_9to5linux_news()
    
    # Merge them all into one flat list
    all_articles = (
        bbc_articles + 
        hn_articles + 
        wh_articles + 
        oann_articles + 
        kernel_articles + 
        linux_articles
    )
    
    # Track the last updated time
    last_updated = datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")
    return render_template("index.html", articles=all_articles, last_updated=last_updated)

if __name__ == "__main__":
    app.run(debug=True)