# Doisense

Aplicație wellbeing: jurnal, chat AI, programe ghidate, plăți Stripe.  
Stack: Nuxt 3, Django REST Framework, PostgreSQL, Redis, Traefik (doar rute pentru acest proiect).

## Documentație

- [docs/architecture.md](docs/architecture.md) – arhitectură, fluxuri
- [docs/database.md](docs/database.md) – schema DB
- [docs/api_design.md](docs/api_design.md) – API
- [docs/coding_rules.md](docs/coding_rules.md) – convenții cod

## Traefik

**Important:** Pe server există și alte proiecte în Traefik. Acest repo **nu modifică** configurația globală Traefik. Doar containerele din `docker-compose.yml` au labels Traefik pentru rutele:

- `https://projects.doimih.net/doisense` → frontend (Nuxt)
- `https://projects.doimih.net/doisense/api` → backend (Django)

Asigură-te că Traefik rulează cu Docker provider și că stack-ul doisense este pe un network vizibil pentru Traefik (ex.: `network: traefik_default` dacă Traefik e în același compose).

## Dezvoltare locală

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # creează .env din exemplu
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Set în `.env` sau în mediu: `NUXT_PUBLIC_APP_BASE_URL=/doisense`, `NUXT_PUBLIC_API_BASE=http://localhost:8000/api` (sau URL-ul backend-ului).

## Docker (producție / staging)

**Pe server:** ca Traefik să routeze traficul la Doisense, containerele trebuie pe același Docker network cu Traefik. Dacă network-ul se numește altfel (ex. `traefik_default`), editează la final din `docker-compose.yml` secțiunea `networks` și pune acel nume. Dacă nu există niciun network Traefik, creează unul și conectează și stack-ul Traefik la el:
```bash
docker network create traefik
```

```bash
docker compose up -d --build
```

Migrări la primul deploy:

```bash
docker compose run --rm backend python manage.py makemigrations
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

Variabile de mediu (în `.env` sau în compose):  
`SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_PREMIUM`, `OPENAI_API_KEY` sau `ANTHROPIC_API_KEY`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`.

## Teste

- **Backend:** `cd backend && pytest`
- **Frontend:** `cd frontend && npm run test`
- **Lint backend:** `ruff check . && black --check .`
- **Lint frontend:** `npm run lint`

## AI – actualizare automată profile

AI scanează textele clienților din DB (jurnal), structurează informația și actualizează singur profilele utilizatorilor (preferred_tone, sensitivities, communication_style, emotional_baseline, keywords), indiferent de limbă/țară.

```bash
# Toți userii cu suficiente intrări în jurnal
docker compose run --rm backend python manage.py ai_update_profiles

# Doar simulare (fără salvare)
docker compose run --rm backend python manage.py ai_update_profiles --dry-run

# Un singur user
docker compose run --rm backend python manage.py ai_update_profiles --user-id=1

# Primele N useri
docker compose run --rm backend python manage.py ai_update_profiles --limit=10
```

Recomandat: cron periodic (ex. zilnic) pentru a reîmprospăta profilele.

## AI Code Reviewer

```bash
# din rădăcina proiectului, cu backend instalat
python scripts/code_reviewer.py path/to/file.py
```

Poate fi integrat în CI (e.g. GitHub Actions) pe PR-uri.

## URL final de verificat

- https://projects.doimih.net/doisense – landing, login/register, chat, jurnal, programe, upgrade premium, i18n (inclusiv poloneză).
