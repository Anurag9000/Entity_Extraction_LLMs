import re
from typing import List, Dict

HONORIFICS = r"(?:Mr|Mrs|Ms|Dr|Shri|Smt|Sri|Prof|M/s)\.?"
ORG_SUFFIX = r"(?:Ltd|Limited|Pvt\.?\s*Ltd\.?|LLP|Inc\.?|Co\.?|Company|Corporation|Enterprises|Technologies)\b"

NAME_PATTERN = re.compile(rf"\b({HONORIFICS}[ \t]+[A-Z][a-zA-Z\-']+(?:[ \t]+[A-Z][a-zA-Z\-']+)*)\b")
ORG_PATTERN = re.compile(rf"\b([A-Z][\w&,.()\-\ ]+[ \t]+{ORG_SUFFIX})", re.IGNORECASE)


def extract_names_orgs(pages: List[Dict]) -> List[Dict]:
    entities = []
    for pg in pages:
        text = pg["text"]
        # Names
        for m in NAME_PATTERN.finditer(text):
            name = m.group(1).strip()
            entities.append({
                "id": None,
                "type": "Name",
                "text": name,
                "normalized_text": name,
                "page": pg["page"],
                "start": m.start(1),
                "end": m.end(1),
                "confidence": 0.7
            })
        # Orgs
        for m in ORG_PATTERN.finditer(text):
            org = m.group(1).strip()
            entities.append({
                "id": None,
                "type": "Organisation",
                "text": org,
                "normalized_text": org,
                "page": pg["page"],
                "start": m.start(1),
                "end": m.end(1),
                "confidence": 0.6
            })
    return entities
