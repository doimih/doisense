#!/usr/bin/env python3
"""
AI Code Reviewer – primește un fișier sau diff și trimite la AI pentru feedback.
Rulează manual sau în CI (e.g. GitHub Actions) pe PR-uri.
Necesită OPENAI_API_KEY sau ANTHROPIC_API_KEY în mediu.
"""
import os
import sys

# Adaugă backend la path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(SCRIPT_DIR, "..", "backend")
sys.path.insert(0, BACKEND)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

PROMPT_TEMPLATE = """Ești code reviewer senior. Analizează acest cod, găsește bug-uri, probleme de arhitectură, stil, securitate. Sugerează îmbunătățiri concrete. Răspunde în română sau engleză, structurat (bullet points).

--- Cod ---
{content}
--- Sfârșit ---
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: code_reviewer.py <file_or_diff>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    prompt = PROMPT_TEMPLATE.format(content=content[:15000])
    # Use Django app for AI call
    import django
    django.setup()
    from ai.router import complete
    reply = complete(prompt, system=None, user_id=None)
    print(reply)


if __name__ == "__main__":
    main()
