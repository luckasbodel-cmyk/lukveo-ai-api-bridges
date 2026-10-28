"""Local validation demo: does not call an AI API."""
from api import gemini_bridge, lukveo_groq_bridge
for label,call in [
    ("Gemini model allowlist",lambda:gemini_bridge.reply("Bonjour",model="not-allowed")),
    ("Groq model allowlist",lambda:lukveo_groq_bridge.ask("not-allowed","Bonjour")),
]:
    try:
        call()
    except ValueError as exc:
        print(f"OK {label}: {exc}")
    else:
        raise AssertionError(label)
print("No network call performed.")
