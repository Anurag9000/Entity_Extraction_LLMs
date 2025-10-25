import re
from typing import List


def _merge_hyphenated(text: str) -> str:
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2\n", text)


def _strip_repeated_headers_footers(pages: List[dict]) -> List[dict]:
    # Very simple heuristic: remove lines that appear on >50% pages
    from collections import Counter
    line_counts = Counter()
    split_pages = []
    for p in pages:
        lines = [ln.strip() for ln in p["text"].splitlines() if ln.strip()]
        split_pages.append(lines)
        for ln in set(lines):
            line_counts[ln] += 1
    threshold = max(2, len(pages)//2)
    out = []
    for p, lines in zip(pages, split_pages):
        filt = [ln for ln in lines if line_counts[ln] <= threshold]
        out.append({"page": p["page"], "text": "\n".join(filt)})
    return out


def normalize_pages(pages: List[dict]) -> List[dict]:
    out = []
    for p in pages:
        t = p["text"]
        t = _merge_hyphenated(t)
        t = re.sub(r"\u00A0", " ", t)
        t = re.sub(r"[\t\r]+", " ", t)
        t = re.sub(r" +", " ", t)
        out.append({"page": p["page"], "text": t})
    out = _strip_repeated_headers_footers(out)
    return out
