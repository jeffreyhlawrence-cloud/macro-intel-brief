import os
import requests
import anthropic
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

TELEGRAM_BOT_TOKEN = os.environ[“TELEGRAM_BOT_TOKEN”]
TELEGRAM_CHAT_ID   = os.environ[“TELEGRAM_CHAT_ID”]
ANTHROPIC_API_KEY  = os.environ[“ANTHROPIC_API_KEY”]
PERPLEXITY_API_KEY = os.environ.get(“PERPLEXITY_API_KEY”, “”)

ANALYSTS = [
“Lyn Alden”,
“Luke Gromen”,
“Bob Elliott”,
“Jim Bianco”,
“Joseph Wang”,
“Cem Karsan”,
“Brent Johnson”,
“Louis Vincent Gave”,
“Andy Constan”,
“Tony Greer”,
“Warren Pies”,
“Harris Kupperman”,
“Keith Dicker”,
“Alex Gurevich”,
“Michael Howell”,
]

# ── Perplexity research (latest views per analyst) ────────────────────────────

def research_analyst_perplexity(analyst: str) -> str:
“”“Use Perplexity to pull the most recent public views for one analyst.”””
if not PERPLEXITY_API_KEY:
return “”
url = “https://api.perplexity.ai/chat/completions”
headers = {
“Authorization”: f”Bearer {PERPLEXITY_API_KEY}”,
“Content-Type”: “application/json”,
}
payload = {
“model”: “sonar”,
“messages”: [
{
“role”: “user”,
“content”: (
f”What are {analyst}’s most recent macro views, tweets, articles, “
“or podcast appearances from the last 7 days? “
“Summarise key themes, asset calls, and notable quotes in 3-5 bullet points. “
“Be concise and factual.”
),
}
],
“max_tokens”: 400,
}
try:
r = requests.post(url, json=payload, headers=headers, timeout=30)
r.raise_for_status()
return r.json()[“choices”][0][“message”][“content”].strip()
except Exception as e:
print(f”Perplexity error for {analyst}: {e}”)
return “”

def research_all_analysts() -> dict[str, str]:
results = {}
for analyst in ANALYSTS:
print(f”  Researching {analyst}…”)
results[analyst] = research_analyst_perplexity(analyst)
return results

# ── Claude synthesis ──────────────────────────────────────────────────────────

def synthesise_brief(raw_research: dict[str, str]) -> str:
“”“Send all raw research to Claude and get a polished daily brief.”””
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

```
research_block = ""
for analyst, notes in raw_research.items():
    research_block += f"\n### {analyst}\n{notes or '(no recent data found)'}\n"

today = datetime.utcnow().strftime("%A, %B %-d %Y")

system_prompt = (
    "You are a senior macro analyst editor. "
    "Your job is to synthesise raw research notes into a crisp, insightful daily brief "
    "that a sophisticated investor would want to read first thing in the morning. "
    "Write in a clear, direct style. No waffle. Prioritise signal over noise."
)

user_prompt = f"""Today is {today}.
```

Below are the latest research notes on 15 macro analysts pulled from the web.
Please produce a **Macro Intelligence Daily Brief** structured as follows:

1. **🌐 Top 3 Macro Themes Today** – the dominant themes cutting across multiple analysts
1. **📊 Analyst Spotlights** – for each analyst with meaningful recent activity, 1-2 sentence summary of their latest view. Skip analysts with no recent data.
1. **⚡ Key Divergences** – where analysts notably disagree and why it matters
1. **🎯 Actionable Signals** – concrete asset/trade ideas mentioned by analysts today
1. **📅 What to Watch** – upcoming catalysts or data points analysts are focused on

Keep the total length under 1,400 words so it fits in a Telegram message.
Use emoji sparingly for section headers only.

-----

RAW RESEARCH:
{research_block}
“””

```
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": user_prompt}],
    system=system_prompt,
)
return message.content[0].text.strip()
```

# ── Telegram delivery ─────────────────────────────────────────────────────────

def send_telegram(text: str) -> None:
“”“Send a message to the configured Telegram chat, splitting if needed.”””
url = f”https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage”
# Telegram max message length is 4096 chars
chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
for chunk in chunks:
payload = {
“chat_id”: TELEGRAM_CHAT_ID,
“text”: chunk,
“parse_mode”: “Markdown”,
}
r = requests.post(url, json=payload, timeout=15)
if not r.ok:
print(f”Telegram error: {r.status_code} {r.text}”)
# Retry without markdown if parse error
payload[“parse_mode”] = “”
requests.post(url, json=payload, timeout=15)

# ── Main ──────────────────────────────────────────────────────────────────────

def run_brief():
print(f”[{datetime.utcnow().isoformat()}] Starting Macro Intelligence Brief…”)

```
print("Step 1/3 – Researching analysts via Perplexity...")
raw = research_all_analysts()

print("Step 2/3 – Synthesising with Claude...")
brief = synthesise_brief(raw)

print("Step 3/3 – Sending to Telegram...")
header = f"📰 *Macro Intelligence Brief* — {datetime.utcnow().strftime('%b %-d, %Y')}\n\n"
send_telegram(header + brief)

print("Done ✓")
```

if **name** == “**main**”:
run_brief()
