# Disaster Recovery Runbook

Acest document descrie pașii minimi pentru backup, validare restore și restore complet pentru proiectul Doisense.

## 1. Prerequisites

- Docker Compose funcțional (docker compose sau docker-compose)
- Serviciul db pornit
- Configurație backup activă în admin (System Configuration -> Backup)
- Credențiale WAL-G valide în configurarea platformei

## 2. Daily Backup

Script:
- scripts/backup.sh

Comandă:
- ./scripts/backup.sh

Ce face:
- Rulează backup WAL-G din containerul db
- Verifică listarea backup-urilor disponibile

Exemplu cron (daily la 02:00 UTC):
- 0 2 * * * /opt/projects/doisense/scripts/backup.sh >> /var/log/doisense-backup.log 2>&1

## 3. Weekly Restore Verification

Script:
- scripts/verify_backup.sh

Comandă:
- ./scripts/verify_backup.sh

Ce face:
- Rulează backup-fetch LATEST într-un director temporar
- Validează integritatea cu pg_controldata
- Șterge datele temporare

Exemplu cron (vineri la 04:00 UTC):
- 0 4 * * 5 /opt/projects/doisense/scripts/verify_backup.sh >> /var/log/doisense-backup-verify.log 2>&1

## 4. Full Restore Procedure

Script:
- scripts/restore_backup.sh

Restore latest backup:
- CONFIRM_RESTORE=yes ./scripts/restore_backup.sh

Restore backup specific:
- CONFIRM_RESTORE=yes ./scripts/restore_backup.sh base_0000000100000000000000AB

Ce face:
- Oprește backend + db
- Golește PGDATA
- Face backup-fetch în PGDATA
- Repornește db + backend

Atenție:
- Este o operațiune distructivă pentru datele curente
- Rulează doar în fereastră de mentenanță aprobată

## 5. Post-Restore Checklist

- Verifică starea serviciilor:
  - docker compose ps
- Verifică loguri db/backend:
  - docker compose logs db --tail=100
  - docker compose logs backend --tail=100
- Rulează verificări aplicație:
  - endpoint auth
  - endpoint chat
  - endpoint payments
- Confirmă date cheie (users/payments/programs) în admin

## 6. Incident Notes

După orice incident DR completează:
- timestamp incident
- backup folosit
- timp total restore
- cauză rădăcină
- acțiuni preventive
