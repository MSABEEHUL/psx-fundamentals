import re

NUM = r"([\-]?\(?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?)"

PL_PATTERNS = {
    "revenue": rf"(?:net\s+sales|sales|revenue)\s+{NUM}",
    "cogs": rf"(?:cost\s+of\s+(?:sales|goods\s+sold))\s+{NUM}",
    "gross_profit": rf"(?:gross\s+profit)\s+{NUM}",
    "admin": rf"(?:administrative\s+expenses?)\s+{NUM}",
    "selling": rf"(?:selling|distribution)\s+expenses?\s+{NUM}",
    "other_income": rf"(?:other\s+income)\s+{NUM}",
    "finance_cost": rf"(?:finance\s+costs?)\s+{NUM}",
    "pbt": rf"(?:profit\s+before\s+tax)\s+{NUM}",
    "tax": rf"(?:taxation|income\s+tax)\s+{NUM}",
    "pat": rf"(?:profit\s+after\s+tax|profit\s+for\s+the\s+period)\s+{NUM}",
    "eps": rf"(?:earnings\s+per\s+share|eps)\s+([\-\(]?\d+(?:\.\d+)?\)?)",
}

def _to_float(s):
    if not s: return None
    s = s.strip()
    neg = s.startswith('(') and s.endswith(')')
    s = s.replace('(', '').replace(')', '').replace(',', '')
    try:
        v = float(s)
        return -v if neg else v
    except:
        return None

def parse_pl_from_text(text):
    blob = re.sub(r"\s+", " ", (text or "").lower())
    out = {}
    for key, pat in PL_PATTERNS.items():
        m = re.search(pat, blob)
        if m:
            out[key] = _to_float(m.group(1))
    if out.get("revenue") and out.get("gross_profit"):
        out["gross_margin_%"] = round(100 * out["gross_profit"] / out["revenue"], 2)
    if out.get("pat") and out.get("revenue"):
        out["net_margin_%"] = round(100 * out["pat"] / out["revenue"], 2)
    if out.get("finance_cost") and out.get("revenue"):
        out["finance_to_sales_%"] = round(100 * out["finance_cost"] / out["revenue"], 2)
    gm = out.get("gross_margin_%", 0)
    nm = out.get("net_margin_%", 0)
    f2s = out.get("finance_to_sales_%", 0)
    score = (0.3 * min(100, gm*2)) + (0.5 * min(100, nm*4)) + (0.2 * max(0, 100 - min(100, f2s*4)))
    out["fundamental_score_0_100"] = round(score, 1)
    return out
