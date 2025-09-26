import io, time, requests, pdfplumber, pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pl_parser import parse_pl_from_text

BASE = "https://dps.psx.com.pk"
ANNOUNCEMENTS_URL = f"{BASE}/announcements"
KEYWORDS = ("financial", "result", "accounts", "quarter", "half year", "annual", "condensed", "audited")

def fetch_html(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text

def list_financial_pdfs(limit=60):
    html = fetch_html(ANNOUNCEMENTS_URL)
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        label = (a.get_text(" ", strip=True) or "").lower()
        if "pdf" in href and any(k in label for k in KEYWORDS):
            full = href if href.startswith("http") else BASE + href
            title = a.get_text(" ", strip=True)
            out.append((title, full))
    seen = set(); uniq=[]
    for t,u in out:
        if u not in seen:
            uniq.append((t,u)); seen.add(u)
    return uniq[:limit]

def download_pdf(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return io.BytesIO(r.content)

def extract_text_first_pages(pdf_bytes, pages=3):
    text = []
    with pdfplumber.open(pdf_bytes) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= pages: break
            text.append(page.extract_text() or "")
    return "\n".join(text)

def run():
    rows = []
    items = list_financial_pdfs()
    for title, url in items:
        try:
            pdf = download_pdf(url)
            text = extract_text_first_pages(pdf, pages=3)
            pl = parse_pl_from_text(text)
            if pl:
                pl["announcement_title"] = title
                pl["source_pdf"] = url
                pl["scraped_at_utc"] = datetime.utcnow().isoformat()
                rows.append(pl)
            time.sleep(0.8)
        except Exception as e:
            print("ERR:", url, e)

    if not rows:
        print("No P&L parsed this run.")
        return

    df = pd.DataFrame(rows).sort_values("scraped_at_utc", ascending=False)

    import os
    os.makedirs("data/history", exist_ok=True)
    df.to_csv("data/latest_psx_pl.csv", index=False)

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    df.to_csv(f"data/history/psx_pl_{stamp}.csv", index=False)
    print("Wrote:", len(df), "rows")

if __name__ == "__main__":
    run()
