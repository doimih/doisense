# Guided Programs

Sistemul de Programe Ghidate extinde aplicatia existenta `programs` si se integreaza direct cu `calendar_tasks`.

## Planuri

- BASIC Start
  - poate lista si deschide programele cu `plan_access=basic`
  - nu poate activa programe
- PREMIUM Flow
  - poate activa programele `basic` si `premium`
  - activarea genereaza task-uri zilnice in calendar
- VIP Executive
  - are tot ce are PREMIUM
  - poate activa si programele `vip`
  - primeste mesaj zilnic adaptiv si recomandare dinamica la completarea zilei

## Seed

Catalogul initial contine 40 de programe in romana:

- 10 wellness
- 10 coaching
- 10 educatie
- 10 suport

Seed-ul este aplicat prin migratia `programs.0007_seed_guided_program_catalog`.

## API

Toate endpoint-urile sunt sub `/api/programs/`.

- `GET /programs?language=ro&category=wellness`
  - returneaza lista programelor accesibile utilizatorului
- `GET /programs/active`
  - returneaza programul activ curent si pasul zilei
- `GET /programs/{id}`
  - returneaza detalii complete si `daily_steps`
- `POST /programs/{id}/activate`
  - activeaza programul si genereaza task-uri calendaristice
- `POST /programs/{id}/complete-day`
  - marcheaza ziua curenta sau ziua ceruta ca finalizata
- `POST /programs/{id}/pause`
  - pune programul pe pauza
- `POST /programs/{id}/resume`
  - reia programul
- `GET /programs/{id}/reflection?day_number=1`
  - citeste reflectia zilei
- `POST /programs/{id}/reflection`
  - salveaza reflectia zilei

## Calendar Integration

Task-urile generate din programe folosesc aceste campuri noi in `calendar_tasks.Task`:

- `source`
- `task_type`
- `guided_program`
- `program_day`

Frontend-ul foloseste aceste campuri pentru a marca task-urile provenite din programe in chat si profil.

## Deploy

Containerele backend si frontend nu monteaza sursa local. Dupa modificari:

1. rulezi migrarile
2. reconstruiesti imaginile backend si frontend
3. repornesti serviciile
