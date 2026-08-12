import json, re, os, datetime, requests, yaml
from bs4 import BeautifulSoup

KEYWORDS = ["최대", "만원", "캐시백", "이벤트", "응모", "결제 기간", "마케팅", "지급일"]

today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d")

with open("config/sources.yml", encoding="utf-8") as f:
    sources = yaml.safe_load(f)["sources"]

offers = []

for s in sources:
    try:
        html = requests.get(
            s["url"],
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        ).text

        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        sentences = re.split(r"(?<=[.!?。])|\s{2,}", text)

        highlights = [
            x for x in sentences
            if any(k in x for k in KEYWORDS)
        ][:12]

        offers.append({
            "company": s["company"],
            "platform": s["platform"],
            "url": s["url"],
            "highlights": highlights,
            "status": "확인됨" if highlights else "요약 부족"
        })

    except Exception as e:
        offers.append({
            "company": s["company"],
            "platform": s["platform"],
            "url": s["url"],
            "highlights": [f"수집 실패: {e}"],
            "status": "실패"
        })

data = {
    "date": today,
    "offers": offers
}

os.makedirs("docs/data", exist_ok=True)
os.makedirs("docs/reports", exist_ok=True)

with open("docs/data/latest.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open(f"docs/reports/{today}.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
