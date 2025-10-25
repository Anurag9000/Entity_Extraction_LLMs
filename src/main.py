import argparse
from pathlib import Path
from src.pdf_loader import extract_pdf_text
from src.text_clean import normalize_pages
from src.detect_pan import detect_pans
from src.ner_rules import extract_names_orgs
from src.link_relations import link_pan_to_person
from src.llm_integration import extract_entities_llm, extract_relations_llm
from src.dedupe import build_entity_index, dedupe_entities
from src.export_csv import export_results
from src.report import write_report


def parse_args():
    p = argparse.ArgumentParser(description="Extract entities and PAN_Of relations from PDF")
    p.add_argument("--pdf", required=True, help="Input PDF file path")
    p.add_argument("--out", required=True, help="Combined CSV output path")
    p.add_argument("--entities", default=None, help="Entities CSV output path")
    p.add_argument("--relations", default=None, help="Relations CSV output path")
    p.add_argument("--report", default=None, help="HTML report output path")
    p.add_argument('--llm', action='store_true', help='Enable LLM-assisted extraction via Ollama')
    p.add_argument('--llm-url', default='http://127.0.0.1:11434', help='Ollama base URL')
    p.add_argument('--llm-model', default='mistral', help='Ollama model name')
    return p.parse_args()


def main():
    args = parse_args()
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = extract_pdf_text(str(pdf_path))
    pages = normalize_pages(pages)

    pan_hits = detect_pans(pages)
    rule_entities = extract_names_orgs(pages)

    # Optional: LLM entities per page
    if args.llm:
        llm_entities = []
        for p in pages:
            llm_entities.extend([
                {'id': None, 'type': e['type'], 'text': e['text'], 'normalized_text': e['text'], 'page': p['page'], 'start': 0, 'end': 0, 'confidence': e.get('confidence', 0.65)}
                for e in extract_entities_llm(args.llm_url, args.llm_model, p['text'])
            ])
        rule_entities += llm_entities

    # Build entity index and dedupe
    entities = rule_entities + [
        {
            "id": None,
            "type": "PAN",
            "text": h["text"],
            "normalized_text": h["text"],
            "page": h["page"],
            "start": h["start"],
            "end": h["end"],
            "confidence": h["confidence"],
        }
        for h in pan_hits
    ]

    entities = dedupe_entities(entities)
    ent_index = build_entity_index(entities)

    relations = link_pan_to_person(pages, entities, ent_index)

    # Optional: LLM relation hints merged in
    if args.llm:
        # Build simple per-page candidate lists and merge
        page_map = {p['page']: p['text'] for p in pages}
        by_page = {}
        for e in entities:
            by_page.setdefault(e['page'], {'PAN': set(), 'Name': set()})
            (by_page[e['page']].setdefault(e['type'], set()).add(e['text']) if e['type'] in ('PAN', 'Name') else None)
        for pg, cand in by_page.items():
            llm_rels = extract_relations_llm(args.llm_url, args.llm_model, page_map.get(pg, ''), sorted(cand.get('PAN', [])), sorted(cand.get('Name', [])))
            # map back by exact text match
            for r in llm_rels:
                pan_id = next((e['id'] for e in entities if e['type']=='PAN' and e['page']==pg and e['text']==r['pan']), None)
                person_id = next((e['id'] for e in entities if e['type']=='Name' and e['page']==pg and e['text']==r['person']), None)
                if pan_id and person_id:
                    relations.append({'subject_id': pan_id, 'relation': 'PAN_Of', 'object_id': person_id, 'confidence': r.get('confidence', 0.7), 'page': pg})

    export_results(entities, relations, args.out, args.entities, args.relations)

    if args.report:
        write_report(entities, relations, args.report)

    print(f"Wrote: {args.out}")
    if args.entities:
        print(f"Wrote: {args.entities}")
    if args.relations:
        print(f"Wrote: {args.relations}")
    if args.report:
        print(f"Wrote: {args.report}")


if __name__ == "__main__":
    main()



