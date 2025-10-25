import re
from typing import List, Dict

PAN_REGEX = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b")


def _valid_pan(p: str) -> bool:
    # PAN basic sanity checks; format ensures most validity
    if len(p) != 10:
        return False
    if not (p[:5].isalpha() and p[5:9].isdigit() and p[9].isalpha()):
        return False
    # Avoid obvious placeholders
    if p in {"AAAAA0000A", "ABCDE1234F"}:
        return False
    return True


def detect_pans(pages: List[Dict]) -> List[Dict]:
    hits = []
    for pg in pages:
        text = pg["text"].upper()
        for m in PAN_REGEX.finditer(text):
            pan = m.group(1)
            if _valid_pan(pan):
                hits.append({
                    "text": pan,
                    "page": pg["page"],
                    "start": m.start(1),
                    "end": m.end(1),
                    "confidence": 0.95
                })
    return hits
