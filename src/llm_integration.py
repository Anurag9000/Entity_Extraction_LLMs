import json
import requests
from typing import List, Dict, Optional


def _ollama_chat(url: str, model: str, messages: List[Dict], temperature: float = 0.2, json_mode: bool = True, stream: bool = False, options: Optional[Dict]=None) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": options or {"temperature": temperature}
    }
    if json_mode:
        payload["format"] = {"type": "object"}
    r = requests.post(url.rstrip("/") + "/api/chat", json=payload, timeout=600)
    r.raise_for_status()
    data = r.json()
    if stream:
        raise NotImplementedError("Streaming not implemented in this client")
    return data.get("message", {}).get("content", "")


def extract_entities_llm(url: str, model: str, page_text: str) -> List[Dict]:
    system = {
        "role": "system",
        "content": (
            "You extract entities from text. Return strict JSON with key 'entities' "
            "as a list of objects: {type: one of [PAN, Name, Organisation], text: string}. "
            "Do not include any other keys. No explanations."
        )
    }
    user = {
        "role": "user",
        "content": (
            "Text:\n" + page_text + "\n\n"
            "Extract entities with types among [PAN, Name, Organisation]."
        )
    }
    raw = _ollama_chat(url, model, [system, user], json_mode=True)
    try:
        obj = json.loads(raw)
        ents = obj.get("entities", [])
        out = []
        for e in ents:
            t = (e.get("type") or "").strip()
            if t not in ("PAN", "Name", "Organisation"):
                continue
            txt = (e.get("text") or "").strip()
            if not txt:
                continue
            out.append({
                "type": t,
                "text": txt,
                "confidence": 0.65
            })
        return out
    except Exception:
        return []


def extract_relations_llm(url: str, model: str, page_text: str, pans: List[str], persons: List[str]) -> List[Dict]:
    system = {
        "role": "system",
        "content": (
            "You link PAN to Person using relation PAN_Of. Return strict JSON: {relations: [{pan: string, person: string}]}"
        )
    }
    user = {
        "role": "user",
        "content": (
            "Text:\n" + page_text + "\n\nPAN candidates: " + ", ".join(pans) + "\nPeople candidates: " + ", ".join(persons)
        )
    }
    raw = _ollama_chat(url, model, [system, user], json_mode=True)
    try:
        obj = json.loads(raw)
        rels = obj.get("relations", [])
        out = []
        for r in rels:
            pan = (r.get("pan") or "").strip()
            person = (r.get("person") or "").strip()
            if pan and person:
                out.append({"pan": pan, "person": person, "confidence": 0.7})
        return out
    except Exception:
        return []
