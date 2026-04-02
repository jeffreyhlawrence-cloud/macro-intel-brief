import os
import requests
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get(‘TELEGRAM_BOT_TOKEN’, ‘’)
TELEGRAM_CHAT_ID   = os.environ.get(‘TELEGRAM_CHAT_ID’, ‘’)
ANTHROPIC_API_KEY  = os.environ.get(‘ANTHROPIC_API_KEY’, ‘’)
PERPLEXITY_API_KEY = os.environ.get(‘PERPLEXITY_API_KEY’, ‘’)

ANALYSTS = [
‘Lyn Alden’,
‘Luke Gromen’,
‘Bob Elliott’,
‘Jim Bianco’,
‘Joseph Wang’,
‘Cem Karsan’,
‘Brent Johnson’,
‘Louis Vincent Gave’,
‘Andy Constan’,
‘Tony Greer’,
‘Warren Pies’,
‘Harris Kupperman’,
‘Keith Dicker’,
‘Alex Gurevich’,
‘Michael Howell’,
]

def research_analyst_perplexity(analyst):
if not PERPLEXITY_API_KEY:
return ‘’
url = ‘https://api.perplexity.ai/chat/completions’
headers = {
‘Authorization’: ’Bearer ’ + PERPLEXITY_API_KEY,
‘Content-Type’: ‘application/json’,
}
payload = {
‘model’: ‘sonar’,
‘messages’: [
{
‘role’: ‘user’,
‘content’: (
’What are ’ + analyst + ’s most recent macro views, tweets, articles, ’
’or podcast appearances from the last 7 days? ’
’Summarise key themes, asset calls, and notable quotes in 3-5 bullet points. ’
‘Be concise and factual.’
),
}
],
‘max_tokens’: 400,
}
try:
r = requests.post(url, json=payload, headers=headers, timeout=30)
r.raise_for_status()
return r.json()[‘choices’][0][‘message’][‘content’].strip()
except Exception as e:
print(’Perplexity error for ’ + analyst + ’: ’ + str(e))
return ‘’

def research_all_analysts():
results = {}
for analyst in ANALYSTS:
print(’  Researching ’ + analyst + ‘…’)
results[analyst] = research_analyst_perplexity(analyst)
return results

def synthesise_brief(raw_research):
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

```
research_block = ''
for analyst, notes in raw_research.items():
    research_block += '\n### ' + analyst + '\n' + (notes or '(no recent data found)') + '\n'

today = datetime.utcnow().strftime('%A, %B %-d %Y')

system_prompt = (
    'You are a senior macro analyst editor. '
    'Your job is to synthesise raw research notes into a crisp, insightful daily brief '
    'that a sophisticated investor would want to read first thing in the morning. '
    'Write in a clear, direct style. No waffle. Prioritise signal over noise.'
)

user_prompt = (
    'Today is ' + today + '.\n\n'
    'Below are the latest research notes on 15 macro analysts pulled from the web.\n'
    'Please produce a Macro Intelligence Daily Brief structured as follows:\n\n'
    '1. Top 3 Macro Themes Today\n'
    '2. Analyst Spotlights\n'
    '3. Key Divergences\n'
    '4. Actionable Signals\n'
    '5. What to Watch\n\n'
    'Keep the total length under 1400 words.\n\n'
    '---\nRAW RESEARCH:\n' + research_block
)

message = client.messages.create(
    model='claude-opus-4-5',
    max_tokens=2000,
    messages=[{'role': 'user', 'content': user_prompt}],
    system=system_prompt,
)
return message.content[0].text.strip()
```

def send_telegram(text):
url = ‘https://api.telegram.org/bot’ + TELEGRAM_BOT_TOKEN + ‘/sendMessage’
chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
for chunk in chunks:
payload = {
‘chat_id’: TELEGRAM_CHAT_ID,
‘text’: chunk,
‘parse_mode’: ‘Markdown’,
}
r = requests.post(url, json=payload, timeout=15)
if not r.ok:
print(’Telegram error: ’ + str(r.status_code) + ’ ’ + r.text)
payload[‘parse_mode’] = ‘’
requests.post(url, json=payload, timeout=15)

def run_brief():
print(‘Starting Macro Intelligence Brief…’)
print(‘Step 1/3 - Researching analysts via Perplexity…’)
raw = research_all_analysts()
print(‘Step 2/3 - Synthesising with Claude…’)
brief = synthesise_brief(raw)
print(‘Step 3/3 - Sending to Telegram…’)
header = ‘Macro Intelligence Brief - ’ + datetime.utcnow().strftime(’%b %-d, %Y’) + ‘\n\n’
send_telegram(header + brief)
print(‘Done’)

if **name** == ‘**main**’:
run_brief()
