# Doisense

Repo tehnic pentru platforma wellbeing (Nuxt 3 + Django REST) cu journaling, AI chat, programe ghidate, plăți Stripe, suport AI și automatizări operaționale.

## Scope tehnic

Sistemul acoperă end-to-end:

- lifecycle utilizator: register, activare email, login JWT, onboarding, trial, upgrade
- AI runtime: jurnal, chat, profilare automată, suport AI contextual
- billing: Stripe upgrade + webhook sync + status endpoint
- engagement automation: reminder-e și recomandări prin comenzi cron
- conformitate: export date și ștergere/anonymizare cont

## Arhitectură

Componente runtime:

- frontend: Nuxt 3, Pinia, i18n, route middleware
- backend: Django + DRF + JWT
- storage: PostgreSQL
- cache/rate-limit: Redis
- edge routing: Traefik (rute dedicate aplicației)

Flux infrastructură:

- https://projects.doimih.net/doisense -> frontend
- https://projects.doimih.net/doisense/api -> backend

Notă: acest repo nu modifică configurația globală Traefik. Rulează doar labels/rute pentru stack-ul Doisense.

## Matrice endpoint-uri principale

Auth și user lifecycle:

- POST /api/auth/register
- POST /api/auth/activate
- POST /api/auth/login
- POST /api/auth/refresh

User self-service:

- GET /api/me
- PATCH /api/me
- DELETE /api/me
- GET /api/me/export

AI și support:

- POST /api/ai/chat
- POST /api/ai/journal
- POST /api/support/ask

Programs:

- GET /api/programs
- GET /api/programs/{id}/days/{day_number}
- GET /api/programs/{id}/progress
- POST /api/programs/{id}/progress

Payments:

- POST /api/payments/upgrade
- GET /api/payments/status
- POST /api/payments/webhook

## Control acces

- autentificare: JWT pentru endpoint-urile private
- paywall: verificări has_paid_access și effective_plan_tier
- support AI: disponibil tuturor userilor autentificați, rate-limited
- programe: acces condiționat de plan/trial activ

## Observații de integrare critice

- endpoint-ul de profil este /api/me, nu /api/auth/me
- onboarding_completed se persistă prin PATCH /api/me
- email SMTP: TLS și SSL sunt mutual exclusive

Config SMTP valid:

- port 587: TLS=true, SSL=false
- port 465: TLS=false, SSL=true

## Admin (Unfold)

Module operaționale relevante:

- CMS Pages
- System Configuration: Localization, Contact and Email, OAuth, Stripe, AI
- Backup Configuration separat pentru WAL-G/S3
- dashboard intern cu KPI și metrici comerciale/operaționale

Metrici dashboard extinse:

- tier_distribution
- mrr_estimate
- churn_rate_30d
- ai_engagement_by_tier

## Automatizări cron

Comenzi disponibile:

- python manage.py expire_trials
- python manage.py send_trial_warnings
- python manage.py send_journal_reminders
- python manage.py send_wellbeing_reminders
- python manage.py send_daily_plan_reminders
- python manage.py send_inactivity_reminders
- python manage.py send_goal_reminders
- python manage.py send_upgrade_recommendations
- python manage.py ai_update_profiles

Script bootstrap cron:

```bash
bash scripts/setup_cron.sh
```

Detalii de scheduling: [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md)

## Frontend reliability flags

Stare curentă pentru stabilitate producție:

- PWA dezactivat temporar în nuxt config
- pagină offline cu flow de recovery
- cleanup automat service worker și cache pentru clienți cu stare stale

## Setup local (dev)

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

Variabile minime utile:

- NUXT_PUBLIC_APP_BASE_URL=/doisense
- NUXT_PUBLIC_API_BASE=http://localhost:8000/api

## Deploy docker

Pornire:

```bash
docker compose up -d --build
```

Primul deploy:

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

Traefik networking: stack-ul trebuie conectat la același network Docker cu Traefik.

## Testing și quality gates

Backend:

```bash
cd backend && pytest
```

Frontend:

```bash
cd frontend && npm run test
```

Lint:

```bash
cd backend && ruff check . && black --check .
cd frontend && npm run lint
```

## Mini runbook incident response

### 1) Auth/login nu funcționează

Check rapid:

- frontend route valid: /doisense/ro/auth/login sau /doisense/auth/login
- backend auth endpoints active: /api/auth/login, /api/auth/refresh
- endpoint profil: /api/me (nu /api/auth/me)

Comenzi utile:

```bash
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 frontend
```

Ce cauți în log-uri:

- 401 masiv după deploy (token invalid/expirat)
- 404 pe /api/auth/me (route greșită în frontend)
- erori CORS/CSRF după schimbări de domeniu

### 2) Chat AI indisponibil sau răspunsuri goale

Check rapid:

- configurare AI în admin (provider, API key)
- acces user: has_paid_access/effective_plan_tier
- endpoint-uri: /api/ai/chat și /api/support/ask

Comenzi utile:

```bash
docker compose logs --tail=200 backend | grep -i -E "ai|openai|anthropic|timeout|429|error"
```

Ce cauți în log-uri:

- timeouts provider AI
- rate limit upstream (429)
- chei API lipsă/greșite

### 3) Payments/upgrade inconsistente

Check rapid:

- variabile Stripe: secret, webhook secret, price IDs
- webhook endpoint: /api/payments/webhook
- status user: /api/payments/status

Comenzi utile:

```bash
docker compose logs --tail=300 backend | grep -i -E "stripe|webhook|payment|subscription"
```

Ce cauți în log-uri:

- semnătură webhook invalidă
- mismatch price ID environment vs admin config
- status payment rămas stale după eveniment Stripe

### 4) Onboarding blocat la ultimul pas

Check rapid:

- PATCH /api/me persistă onboarding_completed
- middleware frontend nu redirecționează în buclă
- clienți blocați pe cache vechi: test în incognito

Comenzi utile:

```bash
docker compose logs --tail=200 backend | grep -i onboarding
docker compose logs --tail=200 frontend
```

Remediere rapidă client-side:

- hard refresh
- clear browser cache
- dacă e nevoie, service worker cleanup (offline recovery flow)

### 5) Offline/PWA comportament anormal

Stare curentă: PWA este dezactivat temporar pentru stabilitate.

Check rapid:

- confirmă că nu rulează service worker stale în browser
- validează pagina /doisense/offline

Comenzi utile:

```bash
docker compose logs --tail=200 frontend
```

### 6) SMTP test email eșuează

Check rapid:

- TLS/SSL mutual exclusive
- port corect (587 TLS, 465 SSL)
- host/user/password valide

Comenzi utile:

```bash
docker compose logs --tail=200 backend | grep -i -E "smtp|email|tls|ssl|wrong version"
```

### Escalation checklist

1. Confirmă impact: auth, ai, payments, onboarding sau email.
2. Colectează loguri backend/frontend din ultimele 10-15 minute.
3. Rulează endpoint health checks manual din browser/API client.
4. Aplică fix minim, redeploy targetat, revalidează fluxul complet.
5. Actualizează docs relevante din folderul docs după incident.

## Inventar complet adăugiri (toate prompturile)

1. Engagement automation și deduplicare livrare notificări
2. Support AI dedicat cu intent classification și context de abonament
3. Program progress model și API GET/POST pe zile completate
4. Separare Backup Configuration de Email settings în admin
5. Hardening onboarding și persistență onboarding_completed prin PATCH /api/me
6. Recovery pentru offline și stale service workers
7. Stabilizare trial/billing lifecycle cu comenzi automate și webhook handling
8. Flux GDPR complet: export date și ștergere/anonymizare cont
9. Script operațional pentru cron bootstrap
10. Extindere dashboard intern cu MRR, churn și engagement pe tier
11. Clarificare și corecție routing API sub prefixul /doisense/api

## Documentație tehnică

- [docs/architecture.md](docs/architecture.md)
- [docs/database.md](docs/database.md)
- [docs/api_design.md](docs/api_design.md)
- [docs/coding_rules.md](docs/coding_rules.md)
- [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md)
- [docs/STEP_12_FINAL_AUDIT.md](docs/STEP_12_FINAL_AUDIT.md)
- [docs/STEP_9_DEVOPS_AUDIT.md](docs/STEP_9_DEVOPS_AUDIT.md)
- [docs/STEP_8_SUPPORT_AI_AUDIT.md](docs/STEP_8_SUPPORT_AI_AUDIT.md)
- [docs/STEP_5_EXECUTIVE_SUMMARY.md](docs/STEP_5_EXECUTIVE_SUMMARY.md)

## URL verificare runtime

- https://projects.doimih.net/doisense
