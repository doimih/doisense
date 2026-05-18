# Audit: Conectare la API Dedicat pentru QA

Data: 2026-03-30

## Obiectiv

Evaluarea platformei pentru conectare la un API dedicat QA, astfel incat sa suporte:
- testele QA deja executate (infrastructura, servicii, performanta, fiabilitate, observabilitate),
- testele viitoare (extensibile, repetabile, environment-aware).

## Rezumat executiv

Concluzie: platforma este pregatita la nivel bun pentru conectare la API dedicat QA, dar are cateva gap-uri operationale ce trebuie standardizate pentru scalare.

Nivel de pregatire estimat: 8/10.

Puncte forte:
- frontend are runtime config pentru `apiBase`.
- backend are configurare de securitate prin env (CORS/CSRF/hosts/cookies).
- exista deja suite automate solide (health, observability, outage, backup verify).
- monitoring stack este operational si validat.

Gap-uri principale:
- lipsa unui contract unificat de rulare smoke pe API extern dedicat QA.
- lipsa unui workflow CI dedicat pentru endpoint QA remote.
- configurari CORS/CSRF trebuie sincronizate explicit pentru domeniul QA.

## Dovezi tehnice (platform readiness)

1) Frontend API endpoint configurabil
- `frontend/nuxt.config.ts` foloseste `NUXT_PUBLIC_API_BASE` in runtimeConfig.
- `frontend/composables/useApi.ts` centralizeaza calls si foloseste `credentials: include`.

2) Backend securizat pentru traffic browser
- `backend/config/settings.py` foloseste CORS/CSRF din env.
- auth pe cookie HttpOnly deja implementat.

3) QA si fiabilitate existente
- `backend/core/tests/test_healthcheck.py`
- `backend/core/tests/test_observability.py`
- `backend/ai/tests/test_outage_flows.py`
- `scripts/verify_backup.sh`

4) Observabilitate operationala
- `docker-compose.monitoring.yml`
- `monitoring/alert_rules.yml`

## Gap Analysis pentru API QA Dedicat

### G1. Configurare environment QA incompleta (Mediu)
Risc:
- routing frontend poate ramane legat de API-ul implicit daca variabila nu este standardizata in deploy.

Status actual:
- frontend permite override prin env.
- compose frontend avea valoare hardcoded pentru API base inainte de acest audit.

Remediere aplicata:
- `docker-compose.yml` a fost actualizat sa foloseasca:
  - `NUXT_PUBLIC_API_BASE: ${NUXT_PUBLIC_API_BASE:-https://projects.doimih.net/doisense/api}`
- `.env.example` a fost actualizat cu `NUXT_PUBLIC_API_BASE`.

### G2. Lipsa smoke-runner dedicat pentru API QA extern (Major)
Risc:
- fara script standard, testele rapide pe API QA devin manuale/inconsistente.

Remediere aplicata:
- Script nou: `scripts/qa_api_smoke.sh`
- Valideaza:
  - `/health`
  - optional login/me/refresh/logout pe baza de credentiale QA
- Suporta endpoint remote prin `API_BASE`.

### G3. Lipsa pipeline CI dedicat QA remote (Major)
Risc:
- testele in CI valideaza codul intern, dar nu valideaza continuu endpoint-ul QA dedicat.

Recomandare:
- adaugare job separat in CI (sau workflow nou) care ruleaza:
  - `scripts/qa_api_smoke.sh`
  - cu secrete `QA_API_BASE`, `QA_EMAIL`, `QA_PASSWORD`.
- rulare recomandata: schedule + manual dispatch + post-deploy QA.

### G4. Contract de date QA lipsa (Mediu)
Risc:
- instabilitate teste din cauza datelor fluctuante.

Recomandare:
- definire set minim de conturi/fixture-uri QA persistente.
- conventionare namespace de date QA pentru cleanup automat.

### G5. Matrice de compatibilitate API pentru viitor (Mediu)
Risc:
- testele noi pot deriva in implementari neuniforme.

Recomandare:
- introducere test matrix pe categorii:
  - smoke,
  - auth lifecycle,
  - quota/rate-limit,
  - resiliency fallback,
  - operational endpoints.

## Ce s-a implementat in urma auditului

1) Parametrizare API in compose frontend
- fisier: `docker-compose.yml`
- schimbare: frontend `NUXT_PUBLIC_API_BASE` -> env override cu fallback sigur.

2) Variabila API in root env example
- fisier: `.env.example`
- adaugat: `NUXT_PUBLIC_API_BASE`.

3) Smoke script pentru API QA dedicat
- fisier nou: `scripts/qa_api_smoke.sh`
- capabilitati:
  - health check mandatory,
  - auth flow optional cu cookie lifecycle.

4) Enforcement IP allowlist configurabil din Admin Settings
- adaugat camp in `SystemConfig`: `qa_allowed_source_ips`
- camp expus in Admin, sectiunea `QA Access`
- middleware activ: `QAIPAllowlistMiddleware`
- comportament:
  - daca lista este goala, accesul API nu este restrictionat,
  - daca lista este populata, endpoint-urile API (exceptand `/api/health`) accepta doar IP/CIDR allowlist,
  - cererile nepermise primesc `403` cu cod `ip_not_allowed`.

## Cum se foloseste API QA dedicat acum

Exemplu fara auth:
```bash
API_BASE=https://qa-api.example.com/doisense/api ./scripts/qa_api_smoke.sh
```

Exemplu cu auth:
```bash
API_BASE=https://qa-api.example.com/doisense/api \
QA_EMAIL=qa.user@example.com \
QA_PASSWORD='strong-password' \
./scripts/qa_api_smoke.sh
```

## Plan recomandat pentru testele care urmeaza

Etapa 1 (imediat):
- operationalizare script smoke in CI remote QA.
- aliniere CORS/CSRF/hosts pentru domeniul QA.

Etapa 2 (scurt termen):
- suite API integration separate de unit tests locale.
- set fixtures QA stabile + cleanup strategy.

Etapa 3 (mediu termen):
- SLO-uri QA API (latency p95, error rate, availability).
- quality gates automate pe performanta si fiabilitate.

## Verdict final

Platforma poate fi conectata in mod robust la un API dedicat QA.

Cu remedierea aplicata in acest audit (parametrizare API + smoke script), baza tehnica este pregatita pentru:
- rerulare consistenta a testelor existente,
- extindere controlata a testelor viitoare,
- integrare graduala in CI/CD pentru validari remote QA continue.
