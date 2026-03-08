# Arhitectura proiectului Doisense

## 1. Prezentare generală

Doisense este o aplicație web de wellbeing (jurnal, chat AI, programe ghidate) cu plăți Stripe și multi-limbă.

## 2. Stack tehnic

| Strat | Tehnologie |
|-------|------------|
| Frontend | Nuxt 3, TypeScript, Pinia, Tailwind, i18n, Jest |
| Backend | Django 5.x, Django REST Framework |
| DB | PostgreSQL |
| Cache | Redis (sessii, rate limiting) |
| Proxy | Traefik (reverse proxy + SSL) – doar rute pentru doisense |
| Containerizare | Docker, Docker Compose |
| AI | GPT-5 Mini + Claude (prin backend) |
| Plăți | Stripe |

## 3. Diagramă high-level

```
[Client] --> Traefik (projects.doimih.net)
                 |
                 +-- /doisense     --> Frontend (Nuxt, port 3000)
                 +-- /doisense/api --> Backend (Django/Gunicorn, port 8000)

Backend --> PostgreSQL
Backend --> Redis
Backend --> AI (OpenAI / Anthropic)
Backend --> Stripe API
```

## 4. Ideea principală AI

AI **scanează DB-ul** cu textele scrise de clienți (jurnal, eventual și conversații viitoare), **structurează informația** și **își face singur update la profilele utilizatorilor** – indiferent din ce țară/limbă sunt. Fluxul:

1. **Colectare:** pentru fiecare user se citesc intrările din jurnal (și alte surse de text, dacă există).
2. **Analiză:** textele (în orice limbă) sunt trimise la AI; acesta extrage ton preferat, sensibilități, stil de comunicare, teme emoționale, cuvinte-cheie.
3. **Actualizare:** câmpurile din `profiles_userprofile` (preferred_tone, sensitivities, communication_style, emotional_baseline, keywords) sunt actualizate automat din răspunsul structurat al AI.
4. **Orchestrare:** se rulează prin management command `ai_update_profiles` (manual sau cron), nu în timp real la fiecare scriere.

Astfel, chat-ul și alte funcții pot folosi un profil mereu proaspăt, personalizat pe baza ce scriu utilizatorii, fără să depindă de țară sau limbă.

## 5. Fluxuri principale

### 5.1 Autentificare
- Register → POST /api/auth/register → User + Profile creat
- Login → POST /api/auth/login → JWT (access + refresh)
- Refresh → POST /api/auth/refresh → nou access token

### 5.2 Chat
- Utilizator trimite mesaj → POST /api/chat/send
- Backend: rate limit (Redis), prompt build (profil + template), AI Router (GPT/Claude), răspuns salvat
- Profilul utilizatorului (actualizat periodic de AI din jurnal) personalizează răspunsurile.

### 5.3 Jurnal
- GET /api/journal/questions → întrebări filtrate pe limbă
- POST /api/journal/entries → entry cu content + emotions (JSON)
- Textele din jurnal sunt sursa principală pentru **AI profile updater** (scan + structurare + update profil).

### 5.4 Programe ghidate
- GET /api/programs → listă programe (premium filtrat după is_premium)
- GET /api/programs/{id}/days/{n} → conținut zi

### 5.5 Plăți
- POST /api/payments/create-checkout-session → Stripe Checkout URL
- Webhook Stripe → checkout.session.completed → is_premium = True; subscription.deleted / payment_failed → is_premium = False

## 6. Traefik (doar pentru Doisense)

- Rutele sunt definite **doar** prin labels pe containerele din docker-compose doisense.
- Nu se modifică configurația globală Traefik a serverului.
- Rule: `PathPrefix(/doisense)` pentru frontend, `PathPrefix(/doisense/api)` pentru backend.
- Frontend folosește `baseURL: /doisense` (Nuxt runtimeConfig).

## 7. Securitate

- JWT în httpOnly cookies sau header Authorization.
- CORS restricționat la domeniul aplicației.
- Rate limiting pe /api/chat/send (Redis).
- Validare Stripe webhook prin STRIPE_WEBHOOK_SECRET.
