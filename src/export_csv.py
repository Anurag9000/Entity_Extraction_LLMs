import pandas as pd
from typing import List, Dict, Optional


def export_results(entities: List[Dict], relations: List[Dict], combined_out: str, entities_out: Optional[str], relations_out: Optional[str]):
    # Entities DataFrame
    ent_df = pd.DataFrame(entities)
    rel_df = pd.DataFrame(relations)

    # Combined format: left_entity,left_type,relation,right_entity,right_type,confidence,source_page
    combined_rows = []
    ent_map = {e["id"]: e for e in entities}
    for r in relations:
        left = ent_map.get(r["subject_id"]) or {}
        right = ent_map.get(r["object_id"]) or {}
        combined_rows.append({
            "left_entity": left.get("text"),
            "left_type": left.get("type"),
            "relation": r.get("relation"),
            "right_entity": right.get("text"),
            "right_type": right.get("type"),
            "confidence": r.get("confidence"),
            "source_page": r.get("page"),
        })
    comb_df = pd.DataFrame(combined_rows)

    comb_df.to_csv(combined_out, index=False)
    if entities_out:
        ent_df.to_csv(entities_out, index=False)
    if relations_out:
        rel_df.to_csv(relations_out, index=False)
