import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import json

def fetch_google_news(query, lang='ko', max_results=5):
    """從 Google News RSS 抓取新聞"""
    try:
        encoded_query = quote_plus(query)
        rss_url = f'https://news.google.com/rss/search?q={encoded_query}&hl={lang}&gl={"KR" if lang == "ko" else "JP"}&ceid={"KR" if lang == "ko" else "JP"}:{lang}'
        
        feed = feedparser.parse(rss_url)
        articles = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:max_results]:
            pub_date = None
            if hasattr(entry, 'published'):
                try:
                    pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    pass
            
            if pub_date is None or pub_date >= cutoff_date:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'source': entry.source.title if hasattr(entry, 'source') else ''
                })
        
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def main():
    print("🦦 Fetching Korean music news...")
    korean_news = fetch_google_news('K-pop 콘서트 음악 공연', 'ko')
    
    if len(korean_news) < 3:
        print("   ⚠️ 音樂新聞不足，改抓韓國熱門新聞...")
        korean_news = fetch_google_news('한국 뉴스', 'ko')
    
    print("🦦 Fetching Japanese music news...")
    japanese_news = fetch_google_news('音楽 コンサート ライブ', 'ja')
    
    if len(japanese_news) < 3:
        print("   ⚠️ 音樂新聞不足，改抓日本熱門新聞...")
        japanese_news = fetch_google_news('日本 ニュース', 'ja')
    
    data = {
        'last_updated': datetime.now().isoformat(),
        'date': datetime.now().strftime("%Y-%m-%d"),
        'korean': korean_news,
        'japanese': japanese_news
    }
    
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ News fetched successfully!")
    print(f"   Korean: {len(korean_news)} articles")
    print(f"   Japanese: {len(japanese_news)} articles")

if __name__ == '__main__':
    main()
