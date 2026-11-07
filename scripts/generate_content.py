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
     格式：{{"beginner": ["第1句中文", "第2句中文", ...], "intermediate": [...], "advanced": [...]}}

2. vocabulary: 10個重要單字（必須出現在文章中），每個包含：
   - word: 單字
   - level: JLPT等級(N5/N4/N3/N2/N1)或TOPIK等級(1/2/3/4/5/6)
   - reading: {"韓文發音" if language == "korean" else "英文拼音"}
   - meaning: 中文意思
   - example: {lang_name}例句
   - exampleCN: 例句中文翻譯

3. grammar: 3個文法重點（必須出現在文章中），每個包含：
   - pattern: 文法句型
   - level: JLPT等級(N5/N4/N3/N2/N1)或TOPIK等級(1/2/3/4/5/6)
   - explanation: 中文說明
   - example: {lang_name}例句
   - exampleCN: 例句中文翻譯

4. quiz: 10題測驗（只有 choice 和 reorder 類型），包含：
   - 7-8題 choice 類型（單字/文法選擇題）
   - 2-3題 reorder 類型（重組句子）
   
   每題格式：
   - type: "choice" | "reorder"
   - question: 題目（繁體中文）
   - 若是 choice: options (陣列), correct (正確選項索引 0-3), explanation (中文解釋)
   - 若是 reorder: words (單字陣列), answer (正確句子，單字間用空格分隔), explanation (中文解釋)


回傳的 JSON 必須包含以下結構：
{{
  "fullContent": {{
    "beginner": "句子1。句子2。",
    "intermediate": "句子1。句子2。",
    "advanced": "句子1。句子2。",
    "original": "{title}",
    "titleTranslation": "標題繁中翻譯",
    "translations": {{
      "beginner": ["句子1中文", "句子2中文"],
      "intermediate": ["句子1中文", "句子2中文"],
      "advanced": ["句子1中文", "句子2中文"]
    }}
  }},
  "vocabulary": [...10個單字物件...],
  "grammar": [...文法物件...],
  "quiz": [...測驗題物件...]
}}











請確保：
- 所有內容必須與音樂、演唱會、音控相關
- 單字和文法必須實際出現在文章中
- 測驗題目要有挑戰性
- translations 必須逐句對應
- 回傳格式必須是有效的 JSON

"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"你是專業的{lang_name}教師，專精於音樂產業相關的語言教學。請以 JSON 格式回覆。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = json.loads(response.choices[0].message.content)
        # Debug: 檢查 titleTranslation
        if "fullContent" in content:
            print(f"  fullContent keys: {list(content["fullContent"].keys())}")
            if "titleTranslation" in content["fullContent"]:
                print(f"  ✓ titleTranslation: {content["fullContent"]["titleTranslation"]}")
            else:
                print(f"  ✗ 沒有 titleTranslation")
        return content
        
    except Exception as e:
        print(f"生成內容時發生錯誤: {e}")
        return None

def process_news_data(news_data):
    """處理新聞資料並生成學習內容"""
    
    result = {
        "last_updated": datetime.now().isoformat(),
        "date": news_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    }
    
    for language in ["korean", "japanese"]:
        if language in news_data and news_data[language].get("news"):
            news_item = news_data[language]["news"]
            
            print(f"\n正在生成 {language} 學習內容...")
            content = generate_learning_content(
                news_item["title"],
                news_item["summary"],
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
                # 韓文單字與文法用 GPT-4o-mini 標註 TOPIK 等級
                # 日文文法用 GPT-4o-mini 標註 JLPT 等級
                if language == 'japanese' and 'grammar' in content:
                    for gram in content['grammar']:
                        if 'level' not in gram or not gram.get('level'):
                            jlpt_level_gpt = get_jlpt_level_gpt(gram['pattern'], gram.get('explanation', ''), is_grammar=True)
                            if jlpt_level_gpt:
                                gram['level'] = jlpt_level_gpt
                if language == 'korean':
                    # 處理單字
                    if 'vocabulary' in content:
                        for vocab in content['vocabulary']:
                            if 'level' not in vocab or not vocab.get('level'):
                                topik_level = get_topik_level_gpt(vocab['word'], vocab.get('meaning', ''))
                                if topik_level:
                                    vocab['level'] = topik_level
                    
                    # 處理文法
                    if 'grammar' in content:
                        for gram in content['grammar']:
                            if 'level' not in gram or not gram.get('level'):
                                topik_level = get_topik_level_gpt(gram['pattern'], gram.get('explanation', ''), is_grammar=True)
                                if topik_level:
                                    gram['level'] = topik_level
                
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

def get_jlpt_level(word):
    """查詢日文單字的 JLPT 等級"""
    import requests
    try:
        url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('data'):
            first_result = data['data'][0]
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


            jlpt_tags = [tag for tag in first_result.get('jlpt', [])]
            if jlpt_tags:
                # 回傳最高等級，例如 "jlpt-n3" -> "N3"
                return jlpt_tags[0].replace('jlpt-', '').upper()
    except:
        pass
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


