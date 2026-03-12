# UPDATE.md

## Scop

Acest fișier consolidează, din toate fișierele .md din folderul docs, ce mai trebuie făcut în proiect.

Surse analizate:
- docs/ANALYTICS_AUDIT.md
- docs/FEATURE_ACCESS_CONTROL_AUDIT.md
- docs/NOTIFICATIONS.md
- docs/ONBOARDING_FLOW_AUDIT.md
- docs/PAYMENT_SECURITY_AUDIT.md
- docs/PROGRAMS_SYSTEM_AUDIT.md
- docs/STEP_10_ANALYTICS_AUDIT.md
- docs/STEP_12_FINAL_AUDIT.md
- docs/STEP_5_EXECUTIVE_SUMMARY.md
- docs/STEP_8_SUPPORT_AI_AUDIT.md
- docs/STEP_9_DEVOPS_AUDIT.md
- docs/api_design.md
- docs/architecture.md
- docs/coding_rules.md
- docs/database.md
- docs/orchestrator_integration.md
- docs/troubleshooting-404.md

## Normalizare (important)

Unele audituri mai vechi raportează lipsuri care sunt deja închise în auditul final:
- Support AI endpoint
- Program progress tracking de bază
- cron setup script
- extinderi dashboard intern

Conform docs/STEP_12_FINAL_AUDIT.md, acestea sunt implementate.

Prin urmare, lista de mai jos păstrează doar ce rămâne relevant/restant.

## Backlog unificat (ce mai trebuie făcut)

### P0 - Critic (stabilitate operațională și risc business)

- [x] Implementare backup complet și verificare restore
  - scripts/backup.sh
  - scripts/verify_backup.sh
  - scripts/restore_backup.sh
  - docs/DISASTER_RECOVERY.md
  - referință: docs/STEP_9_DEVOPS_AUDIT.md

- [x] Implementare monitoring + alerting
  - docker-compose.monitoring.yml
  - monitoring/prometheus.yml
  - monitoring/alert_rules.yml
  - monitoring/alertmanager.yml
  - monitoring/grafana/dashboards/
  - referință: docs/STEP_9_DEVOPS_AUDIT.md

- [x] Payment hardening minim
  - notificări payment failed / expiring / invalid method
  - webhook deduplication (idempotency tracking)
  - rate limiting endpoint-uri checkout/upgrade
  - referință: docs/PAYMENT_SECURITY_AUDIT.md, docs/STEP_5_EXECUTIVE_SUMMARY.md

### P1 - Ridicat (creștere și control produs)

- [x] Analytics end-to-end (platformă + event schema + dashboards)
  - alege platforma (PostHog recomandat)
  - schema evenimente frontend/backend
  - tracking pentru onboarding, chat, journal, programs, payments
  - dashboard-uri: engagement, funnel, cohort retention, revenue
  - referință: docs/ANALYTICS_AUDIT.md, docs/STEP_10_ANALYTICS_AUDIT.md

- [x] Feature access governance complet
  - feature matrix pe tier
  - permission decorators reutilizabili
  - audit logging pentru access attempts (granted/denied)
  - referință: docs/FEATURE_ACCESS_CONTROL_AUDIT.md, docs/STEP_5_EXECUTIVE_SUMMARY.md

- [x] Quota system pentru monetizare
  - model quota + enforcement în views
  - mesaje/CTA la depășire
  - metrici quota în admin
  - referință: docs/STEP_5_EXECUTIVE_SUMMARY.md

### P2 - Mediu (calitate produs și operare)

- [x] Payment lifecycle extins
  - downgrade capability
  - refund event handling
  - subscription sync background job
  - webhook delivery logging + admin inspection
  - referință: docs/PAYMENT_SECURITY_AUDIT.md

- [x] Onboarding enhancements
  - onboarding analytics tracking
  - tier-specific onboarding variants
  - re-onboarding flow pentru feature discovery
  - referință: docs/STEP_5_EXECUTIVE_SUMMARY.md, docs/ONBOARDING_FLOW_AUDIT.md

- [x] Programs advanced UX/analytics (faza 2+)
  - pause/resume
  - reflection + AI feedback
  - dropout/completion analytics per program
  - admin insights per program
  - referință: docs/PROGRAMS_SYSTEM_AUDIT.md

### P3 - Low / Launch+ (optimizare)

- [x] In-app/push notifications (în prezent există email-only)
  - referință: docs/STEP_12_FINAL_AUDIT.md (Known Gaps)

- [x] User-facing support ticket UI
  - support endpoint există; ticket UI rămâne opțional
  - referință: docs/STEP_12_FINAL_AUDIT.md (Known Gaps)

- [x] Localizare non-EN revizie nativă
  - referință: docs/STEP_12_FINAL_AUDIT.md (Known Gaps)

- [x] Creștere acoperire teste pe zone lipsă
  - prioritar: tests pentru program progress API (automat)
  - referință: docs/STEP_12_FINAL_AUDIT.md (Known Gaps)

## Plan de execuție recomandat (succint)

### Sprint 1 (1-2 săptămâni)
- P0 complet (backup, restore drill, monitoring, alerting)
- payment hardening minim (notifications + webhook dedup + rate limit)

### Sprint 2 (1-2 săptămâni)
- analytics fundație (platformă + event schema + primele dashboard-uri)
- feature matrix + permission decorators

### Sprint 3 (1-2 săptămâni)
- quota system
- onboarding enhancements
- payment lifecycle extins

## Definition of Done (cross-team)

- [x] Toate task-urile P0 în producție și testate prin drill
- [x] Dashboard minim operațional (uptime, errors, payment events)
- [x] Analytics funnel registration -> activation -> trial -> upgrade vizibil
- [x] Feature matrix publicată și aplicată consistent în backend
- [x] Update docs după fiecare lot livrat

## Notă finală

Acest fișier este backlog-ul unic derivat din documentația existentă; la orice implementare nouă, actualizarea lui trebuie făcută în paralel cu documentele sursă din folderul docs.
