"""Local, best-effort Gemini usage accounting. No prompts or secrets are stored."""
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB = Path(os.environ.get('LUKVEO_TOKEN_DB', str(Path.home() / 'LUKVEO_TOKEN_MONITOR' / 'usage.sqlite3')))


def record_gemini(model, response, application='JARVIS'):
    """Save provider-reported usage; never interrupt the AI response on logging failure."""
    try:
        usage = getattr(response, 'usage_metadata', None)
        if usage is None:
            return False
        incoming = getattr(usage, 'prompt_token_count', None)
        outgoing = getattr(usage, 'candidates_token_count', None)
        total = getattr(usage, 'total_token_count', None)
        thoughts = getattr(usage, 'thoughts_token_count', None)
        if incoming is None and outgoing is None and total is None:
            return False
        DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(DB), timeout=5) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_utc TEXT NOT NULL,
                provider TEXT NOT NULL,
                application TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                thinking_tokens INTEGER,
                total_tokens INTEGER
            )''')
            conn.execute('''INSERT INTO usage_events
                (recorded_utc,provider,application,model,input_tokens,output_tokens,thinking_tokens,total_tokens)
                VALUES (?,?,?,?,?,?,?,?)''',
                (datetime.now(timezone.utc).isoformat(), 'Gemini', application, str(model)[:100],
                 incoming, outgoing, thoughts, total))
        return True
    except (OSError, sqlite3.Error, ValueError, TypeError):
        return False


def summary(days=30):
    """Read-only aggregated totals; no invented price or provider quota."""
    days = max(1, min(int(days), 365))
    if not DB.is_file():
        return {'ok': True, 'days': days, 'calls': 0, 'rows': [], 'cost_eur': None}
    with sqlite3.connect(str(DB), timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''SELECT provider, application, model, COUNT(*) calls,
            SUM(input_tokens) input_tokens, SUM(output_tokens) output_tokens,
            SUM(thinking_tokens) thinking_tokens, SUM(total_tokens) total_tokens
            FROM usage_events
            WHERE recorded_utc >= strftime('%Y-%m-%dT%H:%M:%S', 'now', ?)
            GROUP BY provider, application, model ORDER BY calls DESC''', (f'-{days} days',)).fetchall()
    data = [dict(r) for r in rows]
    return {'ok': True, 'days': days, 'calls': sum(r['calls'] for r in data), 'rows': data, 'cost_eur': None}


if __name__ == '__main__':
    import json
    print(json.dumps(summary(), ensure_ascii=False, indent=2))
