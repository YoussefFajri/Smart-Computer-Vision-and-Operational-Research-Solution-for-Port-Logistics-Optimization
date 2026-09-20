"""
LLM Report Generator
────────────────────
Generates a natural-language operational summary.

Backends (set LLM_BACKEND in .env):
  template  — Pure Python f-string (no GPU, no API key needed)
  ollama    — Local model via Ollama (e.g. mistral:7b)
  groq      — Groq cloud API (fast, free tier)
"""
from __future__ import annotations

import os
import sys
import json
from datetime import datetime
from typing import Optional

# ── Load config ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from config import LLM_BACKEND, OLLAMA_BASE_URL, OLLAMA_MODEL, GROQ_API_KEY
except ImportError:
    LLM_BACKEND    = os.getenv("LLM_BACKEND", "template")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "mistral:7b")
    GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")


# ── Main entry point ───────────────────────────────────────────────────────────
def generate_summary(data: dict) -> str:
    """
    Generate an operational summary paragraph.

    Args:
        data: {
          "total_containers": int,
          "unloaded":         int,
          "ocr_errors":       int,
          "dock_name":        str,
          "sts_operator":     str,
          "ship_name":        str,
          "anomalies":        list[str],
          "avg_processing_time": float,
          "ocr_success_rate": float,
        }

    Returns:
        French natural-language paragraph.
    """
    backend = LLM_BACKEND.lower()

    if backend == "ollama":
        return _ollama_summary(data)
    elif backend == "groq":
        return _groq_summary(data)
    else:
        return _template_summary(data)


# ── Template backend ──────────────────────────────────────────────────────────
def _template_summary(d: dict) -> str:
    today      = datetime.now().strftime("%d/%m/%Y")
    total      = d.get("total_containers", 0)
    unloaded   = d.get("unloaded", 0)
    errors     = d.get("ocr_errors", 0)
    dock       = d.get("dock_name", "—")
    operator   = d.get("sts_operator", "—")
    ship       = d.get("ship_name", "—")
    anomalies  = d.get("anomalies", [])
    avg_time   = d.get("avg_processing_time", 0.0)
    ocr_rate   = d.get("ocr_success_rate", 100.0)

    anom_text = ""
    if anomalies:
        anom_text = (
            f" {len(anomalies)} identifiant(s) n'ont pas pu être lus automatiquement "
            f"({', '.join(anomalies[:3])}) et nécessitent une vérification manuelle."
        )

    perf_comment = ""
    if ocr_rate >= 95:
        perf_comment = "Les performances OCR sont excellentes."
    elif ocr_rate >= 80:
        perf_comment = "Les performances OCR sont satisfaisantes."
    else:
        perf_comment = "La lisibilité des identifiants doit être améliorée (éclairage, résolution)."

    return (
        f"Le {today}, le quai {dock} a traité {total} conteneur(s) depuis le navire {ship}. "
        f"Le responsable STS {operator} a supervisé l'ensemble des opérations. "
        f"{unloaded} conteneur(s) ont été enregistrés comme déchargés. "
        f"Le taux de réussite OCR est de {ocr_rate:.1f}% avec un temps de traitement moyen "
        f"de {avg_time:.2f}s par image.{anom_text} {perf_comment}"
    )


# ── Ollama backend ────────────────────────────────────────────────────────────
def _ollama_summary(d: dict) -> str:
    try:
        import requests

        prompt = _build_prompt(d)
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"[LLM] Ollama error: {e} — falling back to template")
        return _template_summary(d)


# ── Groq backend ──────────────────────────────────────────────────────────────
def _groq_summary(d: dict) -> str:
    try:
        import requests

        prompt = _build_prompt(d)
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type":  "application/json",
        }
        body = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 300,
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM] Groq error: {e} — falling back to template")
        return _template_summary(d)


# ── Shared prompt ─────────────────────────────────────────────────────────────
def _build_prompt(d: dict) -> str:
    return (
        "Tu es un assistant logistique portuaire. "
        "Génère un rapport opérationnel concis en français (3-4 phrases) "
        "à partir des données suivantes :\n"
        f"{json.dumps(d, ensure_ascii=False, indent=2)}\n\n"
        "Le rapport doit mentionner le quai, le navire, le responsable STS, "
        "le nombre de conteneurs traités, le taux OCR et les anomalies."
    )


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "total_containers": 42,
        "unloaded":         38,
        "ocr_errors":       4,
        "dock_name":        "Quai 3",
        "sts_operator":     "Ahmed Benali",
        "ship_name":        "MSC Rosaria",
        "anomalies":        ["????1234567", "MSCU000000X"],
        "avg_processing_time": 1.23,
        "ocr_success_rate": 90.5,
    }
    print("[LLM Backend:", LLM_BACKEND, "]")
    print(generate_summary(sample))
