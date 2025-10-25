from typing import List, Dict
from rapidfuzz import fuzz


def canonical(text: str) -> str:
    return " ".join(text.strip().lower().replace(".", "").split())


def dedupe_entities(entities: List[Dict]) -> List[Dict]:
    out = []
    next_id = 1
    for e in entities:
        norm = canonical(e["normalized_text"]) if e.get("normalized_text") else canonical(e["text"])
        found = None
        for ex in out:
            if e["type"] != ex["type"]:
                continue
            if e["type"] == "PAN":
                if norm == canonical(ex["normalized_text"]):
                    found = ex
                    break
            else:
                if fuzz.token_sort_ratio(norm, canonical(ex["normalized_text"])) >= 92:
                    found = ex
                    break
        if found:
            # keep best confidence
            found["confidence"] = max(found["confidence"], e.get("confidence", 0.0))
        else:
            e = dict(e)
            e["id"] = f"E{next_id}"
            e["normalized_text"] = norm
            out.append(e)
            next_id += 1
    return out


def build_entity_index(entities: List[Dict]):
    return {e["id"]: e for e in entities}
