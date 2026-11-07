import os
import json
from openai import OpenAI
from datetime import datetime

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=60.0,
    max_retries=2
)

def generate_learning_content(title, summary, language):
    """使用 OpenAI 生成學習內容"""
    
    lang_name = "韓文" if language == "korean" else "日文"
    level_map = {
        "korean": {
            "beginner": "TOPIK I 1級",
            "intermediate": "TOPIK II 3級", 
            "advanced": "TOPIK II 5級"
        },
        "japanese": {
            "beginner": "JLPT N5",
            "intermediate": "JLPT N3",
            "advanced": "JLPT N1"
        }
    }
    
    prompt = f"""你是一位專業的{lang_name}教師，請根據以下新聞標題和摘要，生成完整的學習內容。

新聞標題：{title}
新聞摘要：{summary}

請生成以下內容（必須是有效的 JSON 格式）：

1. fullContent: 根據標題和摘要擴寫完整新聞內容（約150-200字），包含：
   - beginner: {level_map[language]["beginner"]} 程度版本（3-5句）
   - intermediate: {level_map[language]["intermediate"]} 程度版本（5-7句）
   - advanced: {level_map[language]["advanced"]} 程度版本（7-10句）
   - original: 標題的{lang_name}原文
   - titleTranslation: 標題的繁體中文翻譯
   - translations: 陣列，每個元素對應 beginner/intermediate/advanced 各句的繁體中文翻譯
     格式: {{"beginner": ["第1句中文", "第2句中文", ...], "intermediate": [...], "advanced": [...]}}

2. vocabulary: 10個重要單字（必須出現在文章中），每個包含：
   - word: 單字
   - reading: {"韓文發音" if language == "korean" else "英文拼音（romaji）"}
   - meaning: 中文意思
   - example: {lang_name}例句
   - exampleTranslation: 例句的中文翻譯

3. grammar: 5個重要文法點，每個包含：
   - pattern: 文法句型
   - explanation: 用法說明
   - example: {lang_name}例句
   - exampleTranslation: 例句的中文翻譯

4. quiz: 5道測驗題，每題包含：
   - question: 題目（{lang_name}）
   - options: 4個選項陣列
   - correctAnswer: 正確答案（0-3）
   - explanation: 解釋（繁體中文）
   - translation: 題目的中文翻譯

請確保：
- 所有{lang_name}內容使用正確的語法和自然的表達
- 單字和文法必須出現在文章中
- 測驗題目要有挑戰性但不要太難
- 回傳格式必須是有效的 JSON

回傳格式：
{{
  "fullContent": {{"beginner": "...", "intermediate": "...", "advanced": "...", "original": "...", "titleTranslation": "...", "translations": {{"beginner": [...], "intermediate": [...], "advanced": [...]}}}},
  "vocabulary": [...],
  "grammar": [...],
  "quiz": [...]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"你是一位專業的{lang_name}教師，擅長製作學習內容。請以 JSON 格式回應。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        content_text = response.choices[0].message.content.strip()
        
        if content_text.startswith('```json'):
            content_text = content_text[7:]
        if content_text.startswith('```'):
            content_text = content_text[3:]
        if content_text.endswith('```'):
            content_text = content_text[:-3]
        content_text = content_text.strip()
        
        content = json.loads(content_text)
        return content
        
    except Exception as e:
        print(f"生成內容時發生錯誤: {e}")
        return None

def get_jlpt_level(word):
    """查詢日文單字的 JLPT 等級"""
    import requests
    try:
        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('data'):
            first_result = data['data'][0]
            jlpt_tags = [tag for tag in first_result.get('jlpt', [])]
            if jlpt_tags:
                return jlpt_tags[0].replace('jlpt-', '').upper()
    except:
        pass
    return None

def get_jlpt_level_gpt(pattern, explanation, is_grammar=False):
    """使用 GPT-4o-mini 標註日文文法 JLPT 等級"""
    try:
        prompt = f"""請判斷以下日文文法句型的 JLPT 等級（N5/N4/N3/N2/N1）。
只回傳等級代碼，例如：N3

句型：{pattern}
說明：{explanation}

請根據 JLPT 官方考試範圍判斷，只回傳一個等級代碼（N5/N4/N3/N2/N1）。"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10
        )
        
        level_text = response.choices[0].message.content.strip().upper()
        if level_text in ["N5", "N4", "N3", "N2", "N1"]:
            return level_text
        return None
    except Exception as e:
        print(f"❌ GPT 標註 JLPT 等級失敗：{e}")
        return None

def get_topik_level_gpt(word, meaning, is_grammar=False):
    """使用 GPT-4o-mini 標註韓文 TOPIK 等級"""
    try:
        item_type = "文法句型" if is_grammar else "單字"
        prompt = f"""請判斷以下韓文{item_type}的 TOPIK 等級（1-6）。
只回傳數字，例如：3

{item_type}：{word}
意思：{meaning}

請根據 TOPIK 官方考試範圍判斷，只回傳一個數字。"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10
        )
        
        level_text = response.choices[0].message.content.strip()
        if level_text.isdigit() and 1 <= int(level_text) <= 6:
            return level_text
        return None
        
    except Exception as e:
        print(f"❌ GPT 標註 TOPIK 等級失敗：{e}")
        return None

def process_news_data(news_data):
    """處理新聞資料並生成學習內容"""
    
    result = {
        "last_updated": datetime.now().isoformat(),
        "date": news_data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "korean": [],
        "japanese": []
    }
    
    for language in ["korean", "japanese"]:
        if language in news_data and isinstance(news_data[language], list):
            for news_item in news_data[language]:
                print(f"\n正在生成 {language} 學習內容: {news_item.get('title', '')[:50]}...")
                
                content = generate_learning_content(
                    news_item["title"],
                    news_item.get("summary", ""),
                    language
                )
                
                if content:
                    # 日文單字用 Jisho API 查詢 JLPT 等級
                    if language == 'japanese' and 'vocabulary' in content:
                        for vocab in content['vocabulary']:
                            if 'level' not in vocab or not vocab.get('level'):
                                jlpt_level = get_jlpt_level(vocab['word'])
                                if jlpt_level:
                                    vocab['level'] = jlpt_level
                    
                    # 日文文法用 GPT-4o-mini 標註 JLPT 等級
                    if language == 'japanese' and 'grammar' in content:
                        for gram in content['grammar']:
                            if 'level' not in gram or not gram.get('level'):
                                jlpt_level_gpt = get_jlpt_level_gpt(gram['pattern'], gram.get('explanation', ''), is_grammar=True)
                                if jlpt_level_gpt:
                                    gram['level'] = jlpt_level_gpt
                    
                    # 韓文單字與文法用 GPT-4o-mini 標註 TOPIK 等級
                    if language == 'korean':
                        if 'vocabulary' in content:
                            for vocab in content['vocabulary']:
                                if 'level' not in vocab or not vocab.get('level'):
                                    topik_level = get_topik_level_gpt(vocab['word'], vocab.get('meaning', ''))
                                    if topik_level:
                                        vocab['level'] = topik_level
                        
                        if 'grammar' in content:
                            for gram in content['grammar']:
                                if 'level' not in gram or not gram.get('level'):
                                    topik_level = get_topik_level_gpt(gram['pattern'], gram.get('explanation', ''), is_grammar=True)
                                    if topik_level:
                                        gram['level'] = topik_level
                    
                    # 組合新聞與學習內容
                    news_with_content = {
                        **news_item,
                        **content
                    }
                    result[language].append(news_with_content)
                    print(f"✓ {language} 內容生成成功")
                else:
                    print(f"✗ {language} 內容生成失敗")
    
    return result

if __name__ == "__main__":
    with open("data/news.json", "r", encoding="utf-8") as f:
        news_data = json.load(f)
    
    result = process_news_data(news_data)
    
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n✓ 學習內容已更新到 data/news.json")
