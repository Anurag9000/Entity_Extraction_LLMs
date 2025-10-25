from typing import List, Dict
from html import escape


def write_report(entities: List[Dict], relations: List[Dict], out_path: str):
    n_pan = sum(1 for e in entities if e["type"] == "PAN")
    n_name = sum(1 for e in entities if e["type"] == "Name")
    n_org = sum(1 for e in entities if e["type"] == "Organisation")

    rows = []
    rows.append(f"<li>PAN: {n_pan}</li>")
    rows.append(f"<li>Name: {n_name}</li>")
    rows.append(f"<li>Organisation: {n_org}</li>")
    rows.append(f"<li>Relations (PAN_Of): {len(relations)}</li>")

    sample_rel = []
    for r in relations[:20]:
        sample_rel.append(f"<tr><td>{escape(str(r['page']))}</td><td>{escape(str(r['relation']))}</td><td>{escape(str(r['confidence']))}</td></tr>")

    html = f"""
    <html>
    <head><meta charset='utf-8'><title>Extraction Report</title>
    <style>body{{font-family:Arial, sans-serif;}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:4px 8px}}</style>
    </head>
    <body>
      <h2>Extraction Summary</h2>
      <ul>{''.join(rows)}</ul>
      <h3>Sample Relations</h3>
      <table><tr><th>Page</th><th>Relation</th><th>Confidence</th></tr>
      {''.join(sample_rel)}
      </table>
    </body>
    </html>
    """
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
