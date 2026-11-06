import feedparser
import json
from datetime import datetime

def fetch_google_news(query, language='ko'):
    base_url = "https://news.google.com/rss/search"
    params = {
        'q': query,
        'hl': language,
        'gl': 'KR' if language == 'ko' else 'JP',
        'ceid': 'KR:ko' if language == 'ko' else 'JP:ja'
    }
    
    url = f"{base_url}?q={params['q']}&hl={params['hl']}&gl={params['gl']}&ceid={params['ceid']}"
    
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
    korean_news = fetch_google_news('K-pop 콘서트 OR 음악 공연', 'ko')
    
    print("🦦 Fetching Japanese music news...")
    japanese_news = fetch_google_news('音楽 コンサート OR ライブ', 'ja')
    
    data = {
        'last_updated': datetime.now().isoformat(),
        'korean': korean_news[:1],
        'japanese': japanese_news[:1]
    }
    
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ News fetched successfully!")

if __name__ == '__main__':
    main()
