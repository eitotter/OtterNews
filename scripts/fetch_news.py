import feedparser
import json
from datetime import datetime
from urllib.parse import quote_plus

def fetch_google_news(query, language='ko'):
    base_url = "https://news.google.com/rss/search"
    
    # 正確編碼 URL
    encoded_query = quote_plus(query)
    gl = 'KR' if language == 'ko' else 'JP'
    ceid = 'KR:ko' if language == 'ko' else 'JP:ja'
    
    url = f"{base_url}?q={encoded_query}&hl={language}&gl={gl}&ceid={ceid}"
    
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:5]:
            article = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.published if hasattr(entry, 'published') else '',
                'summary': entry.summary if hasattr(entry, 'summary') else '',
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News'
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def main():
    print("🦦 Fetching Korean music news...")
    korean_news = fetch_google_news('K-pop 콘서트 음악 공연', 'ko')
    
    print("🦦 Fetching Japanese music news...")
    japanese_news = fetch_google_news('音楽 コンサート ライブ', 'ja')
    
    # 修正：直接存第一篇新聞，不是陣列
    data = {
        'last_updated': datetime.now().isoformat(),
        'korean': korean_news[0] if korean_news else None,
        'japanese': japanese_news[0] if japanese_news else None
    }
    
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ News fetched successfully!")
    print(f"   Korean: {len(korean_news)} articles")
    print(f"   Japanese: {len(japanese_news)} articles")

if __name__ == '__main__':
    main()
