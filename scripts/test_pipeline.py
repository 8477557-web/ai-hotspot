"""快速测试AI管线——仅处理前5条"""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from config import *

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    raw = json.load(f)

test_items = raw['items'][:5]
print(f'Testing {len(test_items)} items\n')

from openai import OpenAI
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def call(prompt, model=None):
    model = model or DEEPSEEK_SCORE_MODEL
    r = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=500,
    )
    return r.choices[0].message.content

for i, item in enumerate(test_items):
    title = item.get('title', '')
    summary = item.get('summary', '')[:300]
    source = item.get('source_name', '')
    tier = item.get('source_tier', '')

    # Pre-filter
    p1 = f'Determine if this news is AI-related. Reply ONLY JSON: {{"related": true/false, "reason": "short reason"}}\nTitle: {title}\nSummary: {summary}'
    resp1 = call(p1, DEEPSEEK_PRE_FILTER_MODEL)
    resp1 = resp1.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    try:
        r1 = json.loads(resp1)
        print(f'[{i+1}] Filter: {r1.get("related")} | {title[:50]}')
    except:
        print(f'[{i+1}] Filter parse fail, pass through: {resp1[:50]}')
        r1 = {'related': True, 'reason': 'parse_fail'}

    if r1.get('related'):
        # Scoring
        p2 = f'Score this AI news on 5 dimensions (1-10). Reply ONLY JSON: {{"importance": N, "timeliness": N, "actionability": N, "scarcity": N, "virality": N}}\nTitle: {title}\nSource: {source} (tier: {tier})\nSummary: {summary}'
        resp2 = call(p2)
        resp2 = resp2.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        try:
            scores = json.loads(resp2)
            print(f'    Scores: {scores}')
        except:
            print(f'    Score parse fail: {resp2[:60]}')

    time.sleep(0.3)

print('\nTest done! Pipeline works.')
