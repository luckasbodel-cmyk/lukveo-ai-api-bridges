"""Pont Gemini facultatif pour LUKVEO AI PRO. Aucun appel tant que Gemini n'est pas sélectionné."""
import os

ALLOWED_MODELS = {'gemini-3.5-flash-lite', 'gemini-4-argon'}


def ready():
    return bool(os.environ.get('GEMINI_API_KEY', '').strip())


def reply(message, model='gemini-3.5-flash-lite', api_key=None):
    if model not in ALLOWED_MODELS:
        raise ValueError('Modèle Gemini non autorisé')
    if not (api_key or ready()):
        raise RuntimeError('Variable GEMINI_API_KEY absente')
    if not isinstance(message, str) or not message.strip():
        raise ValueError('Message vide')
    if len(message) > 6000:
        raise ValueError('Message trop long pour Gemini')

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError('Installer google-genai dans le Python utilisé par LUKVEO AI PRO') from exc

    try:
        client = genai.Client(api_key=api_key or os.environ['GEMINI_API_KEY'],
                              http_options=types.HttpOptions(timeout=25000))
        result = client.models.generate_content(
            model=model,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=(
                    'Tu es JARVIS, assistant de LUKVEO. Réponds en français, '
                    'avec précision et naturel. Ne prétends pas avoir exécuté '
                    'une action sur le PC si tu ne l’as pas réellement fait. '
                    'Tu peux préparer du texte et des idées, mais tu ne pilotes '
                    'aucune application dans cette conversation.'
                ),
                max_output_tokens=700,
                temperature=0.5,
            ),
        )
        # LUKVEO TOKEN MONITOR : statistiques Gemini, sans secret ni message.
        # L'enregistrement est facultatif et ne doit jamais bloquer JARVIS.
        try:
            from api.lukveo_token_usage import record_gemini
            record_gemini(model, result)
        except Exception:
            pass
        answer = (result.text or '').strip()
        if not answer:
            raise RuntimeError('Gemini n’a pas renvoyé de texte')
        return answer, model
    except Exception as exc:
        # La requête est éventuellement facturable, suivant le projet et le modèle.
        # Ne jamais journaliser la clé API ou le contenu du message.
        raise RuntimeError('Appel Gemini refusé ou indisponible : '+type(exc).__name__) from exc
