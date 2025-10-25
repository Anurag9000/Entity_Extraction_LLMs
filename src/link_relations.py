from typing import List, Dict
import math

WINDOW_CHARS = 200


def _distance(a: int, b: int) -> int:
    return abs(a - b)


def link_pan_to_person(pages: List[Dict], entities: List[Dict], ent_index: Dict) -> List[Dict]:
    # Build page text map for window extraction
    page_map = {p["page"]: p["text"] for p in pages}

    pans = [e for e in entities if e["type"] == "PAN"]
    persons = [e for e in entities if e["type"] == "Name"]

    relations = []
    for pan in pans:
        page_text = page_map.get(pan["page"], "")
        left = max(0, pan["start"] - WINDOW_CHARS)
        right = min(len(page_text), pan["end"] + WINDOW_CHARS)
        # Candidate persons on same page within rough window bounds
        cand = [pr for pr in persons if pr["page"] == pan["page"] and pr["end"] >= left and pr["start"] <= right]
        if not cand:
            # fallback: closest person on same page
            cand = [pr for pr in persons if pr["page"] == pan["page"]]
        if not cand:
            continue
        best = min(cand, key=lambda pr: _distance((pan["start"]+pan["end"])//2, (pr["start"]+pr["end"])//2))
        dist = _distance((pan["start"]+pan["end"])//2, (best["start"]+best["end"])//2)
        confidence = max(0.4, 1.0 - (dist / (WINDOW_CHARS*2))) * 0.9
        relations.append({
            "subject_id": pan["id"],
            "relation": "PAN_Of",
            "object_id": best["id"],
            "confidence": round(confidence, 3),
            "page": pan["page"],
        })
    return relations
