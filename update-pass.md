# Update parole - unde se pun in Dockploy

Acest document rezuma exact ce parole/chei trebuie actualizate pentru productie si unde se configureaza in Dockploy.

## 1) POSTGRES_PASSWORD
- Rol: parola bazei de date PostgreSQL.
- Unde se pune:
  - serviciul `doisense-app` (Environment Variables)
  - serviciul `doisense-monitoring` (Environment Variables)
- Regula: trebuie sa fie aceeasi valoare in ambele servicii.
- Generare recomandata:
  - `openssl rand -hex 24`

## 2) SECRET_KEY
- Rol: cheia secreta Django (sesiuni, semnare, securitate aplicatie).
- Unde se pune:
  - serviciul `doisense-app` (Environment Variables)
- Generare recomandata:
  - `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

## 3) MINIO_ROOT_PASSWORD
- Rol: parola pentru MinIO (storage intern pentru backup).
- Unde se pune:
  - serviciul `doisense-app` (Environment Variables)
- Generare recomandata:
  - `openssl rand -hex 24`

## 4) GRAFANA_ADMIN_PASSWORD
- Rol: parola contului admin din Grafana.
- Unde se pune:
  - serviciul `doisense-monitoring` (Environment Variables)
- Generare recomandata:
  - `openssl rand -hex 16`

## 5) STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET si Price IDs
- Rol: cheile Stripe pentru plati/webhook si maparea completa a planurilor monthly/yearly.
- Unde se pun:
  - serviciul `doisense-app` (Environment Variables)
- Variabile obligatorii:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_PRICE_ID_BASIC`
  - `STRIPE_PRICE_ID_PREMIUM`
  - `STRIPE_PRICE_ID_VIP`
  - `STRIPE_PRICE_ID_BASIC_YEARLY`
  - `STRIPE_PRICE_ID_PREMIUM_YEARLY`
  - `STRIPE_PRICE_ID_VIP_YEARLY`
- Variabila recomandata pentru productie (secret hardening):
  - `ALLOW_DB_STRIPE_SECRETS=false`
- Cum le obtii:
  - Stripe Dashboard -> Developers -> API keys (`STRIPE_SECRET_KEY`)
  - Stripe Dashboard -> Developers -> Webhooks (`STRIPE_WEBHOOK_SECRET`)
  - Stripe Dashboard -> Products -> Prices (toate `STRIPE_PRICE_ID_*`)

## 6) OPENAI_API_KEY si ANTHROPIC_API_KEY
- Rol: chei pentru functionalitatile AI.
- Unde se pun:
  - serviciul `doisense-app` (Environment Variables)
- Cum le obtii:
  - OpenAI platform (`OPENAI_API_KEY`)
  - Anthropic console (`ANTHROPIC_API_KEY`)

## Checklist rapid
- [ ] Genereaza `POSTGRES_PASSWORD`
- [ ] Genereaza `SECRET_KEY`
- [ ] Genereaza `MINIO_ROOT_PASSWORD`
- [ ] Genereaza `GRAFANA_ADMIN_PASSWORD`
- [ ] Copiaza cheile Stripe in env la `doisense-app`
- [ ] Copiaza cheile OpenAI/Anthropic in env la `doisense-app`
- [ ] Verifica din nou ca `POSTGRES_PASSWORD` e identic in `doisense-app` si `doisense-monitoring`

## Recomandari importante
- Nu reutiliza aceeasi parola la toate variabilele.
- Nu salva aceste valori in repository.
- Pastreaza valorile intr-un password manager.
- Dupa modificare de env in Dockploy, ruleaza redeploy la serviciile afectate.
