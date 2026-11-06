import json
import os
from openai import OpenAI
from datetime import datetime

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_learning_content(article, language='korean'):
    lang_name = '韓文' if language == 'korean' else '日文'
    
    prompt = f"""
你是專業的{lang_name}教師。請根據新聞生成學習內容（JSON格式）：

新聞：{article['title']}

包含：
1. fullContent (四個難度版本)
2. vocabulary (10個單字)
3. grammar (2個文法)
4. quiz (8題測驗)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"你是{lang_name}教師"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    print("🦦 Generating content...")
    
    korean_content = None
    if news_data['korean']:
        korean_content = generate_learning_content(news_data['korean'][0], 'korean')
    
    japanese_content = None
    if news_data['japanese']:
        japanese_content = generate_learning_content(news_data['japanese'][0], 'japanese')
    
    final_data = {
        'last_updated': datetime.now().isoformat(),
        'korean': {
            'news': news_data['korean'][0] if news_data['korean'] else None,
            'content': korean_content
        },
        'japanese': {
            'news': news_data['japanese'][0] if news_data['japanese'] else None,
            'content': japanese_content
        }
    }
    
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Content generated!")

if __name__ == '__main__':
    main()
