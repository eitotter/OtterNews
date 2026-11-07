import feedparser
import json
from datetime import datetime, timedelta
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
        one_week_ago = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries:
            # 篩選一週內的文章
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date < one_week_ago:
                    continue
            
            # 限制最多 5 篇
            if len(articles) >= 5:
                break
            
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
    
    # 如果音樂新聞不足，改抓熱門新聞
    if len(korean_news) < 3:
        print("   ⚠️ 音樂新聞不足，改抓韓國熱門新聞...")
        korean_news = fetch_google_news('한국 뉴스', 'ko')
    
    print("🦦 Fetching Japanese music news...")
    japanese_news = fetch_google_news('音楽 コンサート ライブ', 'ja')
    
    # 如果音樂新聞不足，改抓熱門新聞
    if len(japanese_news) < 3:
        print("   ⚠️ 音樂新聞不足，改抓日本熱門新聞...")
        japanese_news = fetch_google_news('日本 ニュース', 'ja')
    
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
