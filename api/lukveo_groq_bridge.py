"""Groq bridge shared by LUKVEO developer tools. Never sends API keys to browsers."""
import json, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ALLOWED={
 'groq_qwen':'qwen/qwen3.8-27b',
 'groq_oss120':'openai/gpt-oss-120b',
 'groq_oss20':'openai/gpt-oss-20b',
}
def _key():
    key=os.environ.get('GROQ_API_KEY','').strip()
    if key:return key
    candidates=[Path(__file__).resolve().parents[1]/'.env',Path(__file__).resolve().parent/'.env']
    for f in candidates:
        if not f.is_file():continue
        for raw in f.read_text(encoding='utf-8-sig').splitlines():
            line=raw.strip()
            if line.startswith('GROQ_API_KEY='):
                return line.split('=',1)[1].strip().strip(chr(34)+chr(39))
    raise RuntimeError('GROQ_API_KEY absente du fichier .env de LUKVEO')
def ask(model, prompt, max_tokens=3500):
    import requests

    if model not in ALLOWED:
        raise ValueError("Modele Groq non autorise")

    if len(prompt) > 110000:
        raise ValueError("Demande trop volumineuse")

    payload = {
        "model": ALLOWED[model],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_completion_tokens": max_tokens,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + _key(),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "Connexion Groq impossible : " + str(exc)
        ) from None

    if not response.ok:
        try:
            error = response.json().get("error", {})
            detail = error.get("message", "Erreur inconnue")
        except ValueError:
            detail = "Reponse HTTP invalide"

        raise RuntimeError(
            f"Groq HTTP {response.status_code} : {detail[:250]}"
        )

    result = response.json()

    return (
        (result.get("choices", [{}])[0].get("message") or {})
        .get("content", "")
        .strip()
    )
