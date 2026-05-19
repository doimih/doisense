# Doisense

Platformă SaaS de wellbeing și productivitate personală — **Nuxt 3** (frontend) + **Django REST Framework** (backend) — cu AI chat multi-modul, journaling, programe ghidate, plăți Stripe, i18n 7 limbi și SEO internațional complet.

**URL producție:** https://projects.doimih.net/doisense  
**API:** https://projects.doimih.net/doisense/api

---

## Cuprins

1. [Arhitectură](#arhitectură)
2. [Funcționalități principale](#funcționalități-principale)
3. [Planuri de abonament](#planuri-de-abonament)
4. [Internaționalizare (i18n)](#internaționalizare-i18n)
5. [SEO și GEO internațional](#seo-și-geo-internațional)
6. [Matrice endpoint-uri API](#matrice-endpoint-uri-api)
7. [Control acces și securitate](#control-acces-și-securitate)
8. [Email tranzacțional](#email-tranzacțional)
9. [Automatizări cron](#automatizări-cron)
10. [Monitoring și observabilitate](#monitoring-și-observabilitate)
11. [Backup și recuperare date](#backup-și-recuperare-date)
12. [Admin (Unfold)](#admin-unfold)
13. [Frontend — stabilitate producție](#frontend--stabilitate-producție)
14. [Setup local (dev)](#setup-local-dev)
15. [Deploy Docker](#deploy-docker)
16. [Testing și quality gates](#testing-și-quality-gates)
17. [Mini runbook incident response](#mini-runbook-incident-response)
18. [Documentație tehnică](#documentație-tehnică)

---

## Arhitectură

### Componente runtime

| Componentă | Tehnologie | Detalii |
|---|---|---|
| Frontend | Nuxt 3 + Pinia + i18n | SSR, TypeScript strict, Tailwind CSS |
| Backend | Django 5 + DRF + JWT | Python 3.12, HttpOnly cookie auth |
| Baza de date | PostgreSQL 16 | Schema migrată prin Django ORM |
| Cache / Rate-limiting | Redis 7 | Sesiuni, throttle, cozi async |
| Object storage | MinIO (S3-compatible) | Media, backup-uri WAL-G |
| Edge routing | Traefik | Rute per-serviciu cu labels Docker |
| Monitoring | Prometheus + Grafana + Alertmanager | Metrici, dashboards, alerte |

### Flux infrastructură

```
https://projects.doimih.net/doisense      →  frontend (Nuxt SSR)
https://projects.doimih.net/doisense/api  →  backend (DRF)
```

> Acest repo nu modifică configurația globală Traefik — rulează doar labels/rute pentru stack-ul Doisense.

---

## Funcționalități principale

### Lifecycle utilizator
- Înregistrare + activare email cu token one-time
- Login JWT (HttpOnly cookie, refresh automat)
- Onboarding pas-cu-pas (persistat prin `PATCH /api/me`)
- Trial 14 zile cu auto-expirare și avertizare
- Upgrade plan cu Stripe (one-click, webhook sync)
- Export date GDPR + ștergere/anonymizare cont

### AI Chat (4 module)
- **Journal AI** — analiză jurnal, reflecții zilnice, pattern recognition
- **Chat AI** — conversații libere de wellbeing cu context de profil
- **Support AI** — clasificare intent, răspunsuri contextuale bazate pe abonament
- **Profile Updater** — actualizare automată a profilului cognitiv din interacțiuni

### Wellbeing check-in și jurnal
- Intrări zilnice de jurnal cu scoruri de dispoziție
- Remindere personalizate (e-mail + sistem notificări intern)
- Statistici și tendințe pe termen lung

### Programe ghidate
- Programe structurate pe zile (conținut CMS-driven)
- Tracking progres per utilizator
- Acces condiționat de tier de abonament

### Notificări
- Sistem intern de notificări (feed + badge)
- Tipuri: reminder jurnal, reminder wellbeing, reminder plan zilnic, inactivitate, recomandare upgrade, avertizare trial
- Livrare cu deduplicare per eveniment

### Calendar și taskuri
- Taskuri zilnice asociate programelor
- Integrare cu modulul de jurnal

### Plăți Stripe
- Upgrade one-click de la orice tier inferior
- Webhook listener securizat cu validare semnătură
- Sincronizare automată status plată → tier utilizator
- Endpoint status abonament curent

### CMS integrat
- Pagini statice editabile din admin (legal, landing, etc.)
- SEO meta pe pagini CMS

---

## Planuri de abonament

| Plan | Preț | AI Chat | Programe | Support AI |
|---|---|---|---|---|
| **Free** | €0/lună | Limitat | — | Limitat |
| **Trial** | €0 (14 zile) | Complet | Complet | Complet |
| **Basic** | €12/lună | Complet | Complet | Standard |
| **Premium** | €25/lună | Complet | Complet | Prioritar |
| **VIP** | €49/lună | Nelimitat | Complet | Dedicat |

---

## Internaționalizare (i18n)

Limbi suportate (Nuxt i18n, strategie `prefix_except_default`):

| Cod | Limbă | Prefix URL |
|---|---|---|
| `en` | Engleză | *(default, fără prefix)* |
| `ro` | Română | `/ro/` |
| `de` | Germană | `/de/` |
| `fr` | Franceză | `/fr/` |
| `it` | Italiană | `/it/` |
| `es` | Spaniolă | `/es/` |
| `pl` | Poloneză | `/pl/` |

Fișiere de traduceri: `frontend/locales/{en,ro,de,fr,it,es,pl}.json`

---

## SEO și GEO internațional

### robots.txt dinamic
Generat server-side prin Nitro (`frontend/server/routes/robots.txt.ts`):
- `Allow` pentru toate rutele publice indexabile
- `Disallow` pentru rute private: `/auth`, `/onboarding`, `/profile`, `/notifications`, `/tickets`, `/chat`, `/journal`, `/programs`, `/payment-success`, `/trial-expired`
- Directivă `Sitemap:` inclusă automat

### sitemap.xml dinamic
Generat server-side (`frontend/server/routes/sitemap.xml.ts`):
- Toate paginile publice × toate cele 7 limbi
- Taguri `<xhtml:link rel="alternate">` pentru fiecare variantă de limbă
- Tag `x-default` pointând la versiunea engleză

### Hreflang + canonical
Implementate în `frontend/composables/usePublicSeo.ts`:
- `<link rel="alternate" hreflang="...">` injectat în `<head>` pe toate paginile publice
- `<link rel="canonical">` per pagină și limbă
- `x-default` → ruta en pentru motoarele de căutare internaționale

### JSON-LD (Schema.org)
Scheme structurate per pagină:

| Pagină | Schema |
|---|---|
| `/` (Homepage) | `WebSite`, `Organization`, `WebPage` |
| `/pricing` | `Product` cu `Offer` pentru Basic/Premium/VIP |
| `/about` | `AboutPage`, `Organization` |
| `/contact` | `ContactPage`, `ContactPoint` |
| `/faq` | `CollectionPage` |

### Pagini publice indexabile

```
/ /features /pricing /about /contact /faq
/legal/privacy /legal/terms /legal/cookies
/legal/gdpr /legal/ai-consent /legal/payments-subscriptions
```

---

## Matrice endpoint-uri API

### Auth și user lifecycle

| Metodă | Endpoint | Descriere |
|---|---|---|
| POST | `/api/auth/register` | Înregistrare cont nou |
| POST | `/api/auth/activate` | Activare email cu token |
| POST | `/api/auth/login` | Login → set HttpOnly cookie JWT |
| POST | `/api/auth/refresh` | Refresh token acces |
| POST | `/api/auth/logout` | Invalidare sesiune |
| GET | `/api/me` | Profil utilizator curent |
| PATCH | `/api/me` | Actualizare profil / onboarding_completed |
| DELETE | `/api/me` | Ștergere / anonymizare cont |
| GET | `/api/me/export` | Export date GDPR |

### AI

| Metodă | Endpoint | Descriere |
|---|---|---|
| POST | `/api/ai/chat` | Chat wellbeing cu context profil |
| POST | `/api/ai/journal` | Analiză jurnal |
| POST | `/api/support/ask` | Support AI cu clasificare intent |

### Jurnal

| Metodă | Endpoint | Descriere |
|---|---|---|
| GET | `/api/journal` | Listă intrări |
| POST | `/api/journal` | Intrare nouă |
| GET | `/api/journal/{id}` | Detaliu intrare |
| PATCH | `/api/journal/{id}` | Actualizare |
| DELETE | `/api/journal/{id}` | Ștergere |

### Programe ghidate

| Metodă | Endpoint | Descriere |
|---|---|---|
| GET | `/api/programs` | Listă programe disponibile |
| GET | `/api/programs/{id}/days/{day}` | Conținut zi |
| GET | `/api/programs/{id}/progress` | Progres utilizator |
| POST | `/api/programs/{id}/progress` | Marchează zi completată |

### Notificări

| Metodă | Endpoint | Descriere |
|---|---|---|
| GET | `/api/notifications` | Notificări utilizator |
| PATCH | `/api/notifications/{id}/read` | Marchează citit |
| POST | `/api/notifications/read-all` | Marchează toate citite |

### Plăți

| Metodă | Endpoint | Descriere |
|---|---|---|
| POST | `/api/payments/upgrade` | Inițiere upgrade Stripe |
| GET | `/api/payments/status` | Status abonament curent |
| POST | `/api/payments/webhook` | Webhook Stripe (semnătură verificată) |

### Analytics și QA

| Metodă | Endpoint | Descriere |
|---|---|---|
| POST | `/api/analytics/track` | Event tracking frontend |
| GET | `/api/qa/allowed-ips` | Listă IP-uri QA autorizate (admin) |

---

## Control acces și securitate

### Autentificare
- JWT cu HttpOnly cookies (access + refresh)
- Refresh automat transparent pe frontend
- CORS strict: origini explicite, no wildcard în producție

### Autorizare
- `has_paid_access` + `effective_plan_tier` per utilizator
- Middleware Nuxt: redirect automat la login/onboarding/trial-expired
- Rate limiting Redis pe endpoint-urile AI și auth

### Securitate transport
- HSTS activat (1 an, includeSubDomains)
- `Secure; SameSite=Lax` pe toate cookie-urile
- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`
- `Content-Security-Policy` configurabil din admin

### QA IP Allowlist
- Lista IP-uri QA configurabilă din admin (`SystemConfig.qa_allowed_source_ips`)
- Endpoint dedicat `/api/qa/allowed-ips` cu verificare admin

### GDPR
- Export complet date utilizator
- Ștergere/anonymizare cont la cerere
- Consent form pentru date AI (`/legal/ai-consent`)

---

## Email tranzacțional

Sistem HTML email (`backend/core/email_templates.py`):
- Template responsive: titlu, corp text, buton CTA
- Folosit pentru: activare cont, reset parolă, avertizare trial, notificări sistem
- Config SMTP din `SystemConfig` admin

**Notă SMTP importantă:**
```
Port 587 → EMAIL_USE_TLS=True,  EMAIL_USE_SSL=False
Port 465 → EMAIL_USE_TLS=False, EMAIL_USE_SSL=True
```

---

## Automatizări cron

| Comandă | Descriere |
|---|---|
| `python manage.py expire_trials` | Expiră trial-urile scadente |
| `python manage.py send_trial_warnings` | Avertizare 3/1 zile înainte de expirare |
| `python manage.py send_journal_reminders` | Reminder jurnal zilnic |
| `python manage.py send_wellbeing_reminders` | Reminder check-in wellbeing |
| `python manage.py send_daily_plan_reminders` | Reminder plan zilnic program |
| `python manage.py send_inactivity_reminders` | Reminder inactivitate |
| `python manage.py send_goal_reminders` | Reminder obiective |
| `python manage.py send_upgrade_recommendations` | Recomandare upgrade tier |
| `python manage.py ai_update_profiles` | Actualizare automată profiluri cognitive AI |

Bootstrap cron:

```bash
bash scripts/setup_cron.sh
```

Detalii scheduling: [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md)

---

## Monitoring și observabilitate

Stack (`docker-compose.monitoring.yml`):

| Serviciu | Port intern | Rol |
|---|---|---|
| Prometheus | 9090 | Colectare metrici |
| Grafana | 3001 | Dashboards vizuale |
| Alertmanager | 9093 | Routing alerte (email/Slack) |

Fișiere config: `monitoring/prometheus.yml`, `monitoring/alert_rules.yml`, `monitoring/alertmanager.yml`

Dashboards Grafana: `monitoring/grafana/`

### KPI dashboard intern (admin Django)

- `tier_distribution` — distribuție utilizatori per plan
- `mrr_estimate` — MRR estimat
- `churn_rate_30d` — churn în ultimele 30 zile
- `ai_engagement_by_tier` — utilizare AI per tier

---

## Backup și recuperare date

### MinIO (object storage local)
- Stocare media și backup-uri WAL-G PostgreSQL
- Configurabil din admin (`BackupConfiguration`)

### Script-uri operaționale

```bash
bash scripts/backup.sh           # Backup manual DB → MinIO
bash scripts/verify_backup.sh    # Verificare integritate backup
bash scripts/restore_backup.sh   # Restaurare din backup
```

Runbook complet: [docs/DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md)

---

## Admin (Unfold)

Module disponibile în `/doisense/api/admin/`:

- **Users** — gestionare conturi, tier manual, istoric plăți
- **CMS Pages** — pagini statice editabile cu meta SEO
- **System Configuration** — Localization, Contact & Email, OAuth, Stripe, AI, CSP
- **Backup Configuration** — WAL-G / S3 settings (separat de Email)
- **Notificări** — vizualizare și trimitere manuală
- **Programe** — management conținut programe ghidate
- **QA Allowed IPs** — lista IP-uri QA autorizate
- **Dashboard** — KPI comerciale și operaționale

---

## Frontend — stabilitate producție

- **PWA:** dezactivat temporar pentru stabilitate (fără service worker în producție)
- **Pagină offline:** `/doisense/offline` cu flow recovery
- **Cleanup automat SW:** clienți cu stare stale primesc cleanup + reload
- **Auto-recovery chunk errors:**
  - Clear cache + reload o singură dată
  - Fallback redirect controlat → login (`reason=client_recovery`) dacă recovery eșuează
  - Telemetrie best-effort → `/api/analytics/track` (`frontend_chunk_recovery_triggered`, `frontend_chunk_recovery_failed`)

---

## Setup local (dev)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm run dev
```

### Variabile de mediu minime

```env
# Frontend
NUXT_PUBLIC_APP_BASE_URL=/doisense
NUXT_PUBLIC_API_BASE=http://localhost:8000/api
NUXT_PUBLIC_SITE_URL=https://projects.doimih.net

# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/doisense
REDIS_URL=redis://localhost:6379/0
```

---

## Deploy Docker

### Pornire stack complet

```bash
docker compose up -d --build
```

### Primul deploy

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

### Monitoring

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

### Networking

Stack-ul trebuie conectat la același network Docker cu Traefik:
```yaml
networks:
  traefik_public:
    external: true
```

Detalii config: [config-dockploy.md](config-dockploy.md)

---

## Testing și quality gates

### Backend

```bash
cd backend && pytest
# sau în container:
docker compose exec backend pytest
```

### Frontend

```bash
cd frontend && pnpm run test
cd frontend && pnpm run typecheck
```

### Lint

```bash
# Backend
cd backend && ruff check . && black --check .

# Frontend
cd frontend && pnpm run lint
```

### Smoke test API

```bash
API_BASE=https://projects.doimih.net/doisense/api \
QA_EMAIL=qa@example.com \
QA_PASSWORD='password' \
./scripts/qa_api_smoke.sh
```

---

## Mini runbook incident response

### 1. Auth / login nu funcționează

- Frontend route valid: `/doisense/ro/auth/login` sau `/doisense/auth/login`
- Endpoint profil corect: `/api/me` (nu `/api/auth/me`)
- Verificare cookie HttpOnly în DevTools → Application → Cookies

```bash
docker compose logs --tail=200 backend | grep -iE "401|403|auth|jwt"
docker compose logs --tail=200 frontend
```

### 2. Chat AI indisponibil sau răspunsuri goale

- Configurare provider AI în admin (key, model)
- Verificare `has_paid_access` / `effective_plan_tier` pe cont

```bash
docker compose logs --tail=200 backend | grep -iE "ai|openai|anthropic|timeout|429|error"
```

### 3. Payments / upgrade inconsistente

- Variabile Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, price IDs
- Webhook endpoint: `POST /api/payments/webhook`

```bash
docker compose logs --tail=300 backend | grep -iE "stripe|webhook|payment|subscription"
```

### 4. Onboarding blocat la ultimul pas

- `PATCH /api/me` cu `{"onboarding_completed": true}` nu persistă
- Middleware frontend nu redirecționează în buclă
- Test în incognito (cache vechi)

```bash
docker compose logs --tail=200 backend | grep -i onboarding
```

### 5. SMTP email eșuează

- TLS/SSL sunt mutual exclusive (port 587 → TLS, port 465 → SSL)
- Verificare host/user/password în `SystemConfig` admin

```bash
docker compose logs --tail=200 backend | grep -iE "smtp|email|tls|ssl|wrong version"
```

### 6. SEO / robots / sitemap indisponibile

- Endpoint-uri generate dinamic de Nitro (nu fișiere statice)
- Verificare build frontend: `nuxt build` trebuie completat cu succes

```bash
curl https://projects.doimih.net/doisense/robots.txt
curl https://projects.doimih.net/doisense/sitemap.xml
```

### Escalation checklist

1. Confirmă impactul: auth, ai, payments, onboarding, email sau SEO
2. Colectează loguri backend/frontend din ultimele 10-15 minute
3. Rulează endpoint health checks manual (browser sau API client)
4. Aplică fix minim, redeploy targetat, revalidează fluxul complet
5. Actualizează docs relevante din `/docs/` după incident

---

## Documentație tehnică

| Document | Conținut |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Arhitectură sistem, diagrame flux |
| [docs/database.md](docs/database.md) | Schema DB, modele principale |
| [docs/api_design.md](docs/api_design.md) | Convenții API, autentificare, erori |
| [docs/coding_rules.md](docs/coding_rules.md) | Reguli de cod, style guide |
| [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md) | Sistem notificări, scheduling cron |
| [docs/GUIDED_PROGRAMS.md](docs/GUIDED_PROGRAMS.md) | Programe ghidate, structură zile |
| [docs/FEATURE_MATRIX.md](docs/FEATURE_MATRIX.md) | Matrice funcționalități per plan |
| [docs/DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md) | Backup, restore, WAL-G |
| [docs/ANALYTICS_AUDIT.md](docs/ANALYTICS_AUDIT.md) | Analytics events, schema |
| [docs/PAYMENT_SECURITY_AUDIT.md](docs/PAYMENT_SECURITY_AUDIT.md) | Audit securitate plăți |
| [docs/SECURITY_HARDENING_IMPLEMENTED_2026-03-12.md](docs/SECURITY_HARDENING_IMPLEMENTED_2026-03-12.md) | Hardening securitate aplicat |
| [docs/STEP_12_FINAL_AUDIT.md](docs/STEP_12_FINAL_AUDIT.md) | Audit final platformă |
| [docs/STEP_9_DEVOPS_AUDIT.md](docs/STEP_9_DEVOPS_AUDIT.md) | Audit DevOps / CI-CD |
| [docs/STEP_8_SUPPORT_AI_AUDIT.md](docs/STEP_8_SUPPORT_AI_AUDIT.md) | Audit Support AI |
| [docs/STEP_5_EXECUTIVE_SUMMARY.md](docs/STEP_5_EXECUTIVE_SUMMARY.md) | Executive summary |
| [docs/CI_CD_IMPROVEMENTS.md](docs/CI_CD_IMPROVEMENTS.md) | Îmbunătățiri pipeline CI/CD |
