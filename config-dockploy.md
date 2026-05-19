# Configurare Dockploy — Doisense Producție

## Cuprins
1. [Premize — ce trebuie să existe înainte](#1-premize)
2. [Stack 1: Aplicația (docker-compose.yml)](#2-stack-1-aplicatia)
3. [Stack 2: Monitoring (docker-compose.monitoring.yml)](#3-stack-2-monitoring)
4. [Variabilele de mediu (Environment Variables)](#4-variabilele-de-mediu)
5. [Comenzile obligatorii după primul deploy](#5-comenzi-obligatorii-dupa-primul-deploy)
6. [Verificare că totul funcționează](#6-verificare)
7. [GitHub Actions — Environments și Secrets](#7-github-actions)

---

## 1. Premize

Înainte de a configura orice în Dockploy, acestea trebuie să existe deja:

- [ ] Serverul de producție este pornit și ai acces SSH la el
- [ ] Dockploy este instalat pe server (urmezi instrucțiunile de pe dockploy.com)
- [ ] Domeniul `doisense.eu` are un **A record** îndreptat spre IP-ul serverului
  - Se face din panoul DNS al furnizorului de domeniu
  - Poate dura până la 24h să se propage
- [ ] Repo-ul GitHub `doimih/doisense` există și branch-ul `prod` este creat
- [ ] Traefik este pornit pe server (Dockploy îl instalează automat)

---

## 2. Stack 1: Aplicația

### 2.1 Creare proiect în Dockploy

1. Intri în Dockploy → **Projects** → **Create Project**
2. Nume: `doisense-production`
3. Salvezi

### 2.2 Creare serviciu Docker Compose

1. În proiectul creat → **Create Service** → **Docker Compose**
2. Completezi:
   - **Name**: `doisense-app`
   - **Repository URL**: `https://github.com/doimih/doisense`
   - **Branch**: `prod`
   - **Docker Compose File**: `docker-compose.yml`
3. La secțiunea **Environment Variables** copiezi tot blocul din [Secțiunea 4](#4-variabilele-de-mediu)
4. Apeși **Save** (NU Deploy încă — mai întâi trebuie volumele)

### 2.3 Creare volume (obligatoriu înainte de primul Deploy)

Mergi în Dockploy → **Volumes** → **Create Volume** și creezi fiecare:

| Nume volum | Folosit de | Date stocate |
|---|---|---|
| `doisense_pgdata` | Containerul `db` | Baza de date PostgreSQL — **cel mai important** |
| `doisense_media` | Containerul `backend` | Fișierele încărcate de utilizatori (poze, documente) |
| `doisense_backup_data` | Containerul `minio` | Backup-urile bazei de date |

> **Atenție**: Dacă nu creezi volumele înainte, la primul Deploy datele nu vor fi persistente și se pierd la restart.

### 2.4 Pornirea serviciului

1. Te întorci la serviciul `doisense-app` → **Deploy**
2. Dockploy va:
   - Descărca codul din branch `prod`
   - Construi imaginile Docker (durează 5–15 minute prima oară)
   - Porni toate containerele: `db`, `redis`, `backend`, `frontend`, `minio`, `minio-init`
3. Verifici că toate containerele au status **Running** (nu Restarting sau Error)

---

## 3. Stack 2: Monitoring

### 3.1 Creare serviciu separat pentru monitoring

1. În același proiect `doisense-production` → **Create Service** → **Docker Compose**
2. Completezi:
   - **Name**: `doisense-monitoring`
   - **Repository URL**: `https://github.com/doimih/doisense`
   - **Branch**: `prod`
   - **Docker Compose File**: `docker-compose.monitoring.yml`
3. La **Environment Variables** adaugi doar:
   ```
   POSTGRES_PASSWORD=<aceeasi_parola_ca_la_app>
   APP_INTERNAL_NETWORK=doisense_app_internal
   GRAFANA_ADMIN_USER=admin
   GRAFANA_ADMIN_PASSWORD=<parola_puternica_grafana>
   ```
4. Apeși **Save**

### 3.2 Volume pentru monitoring

Creezi în Dockploy → **Volumes**:

| Nume volum | Folosit de | Date stocate |
|---|---|---|
| `prometheus_data` | Containerul `prometheus` | Metrici istorice (15 zile retenție) |
| `grafana_data` | Containerul `grafana` | Dashboard-uri și configurații Grafana |

> **Alertmanager** nu are volum persistent — dacă containerul se restartează, silences-urile se pierd (comportament acceptabil).

### 3.3 Pornire monitoring

→ **Deploy** pe serviciul `doisense-monitoring`

Containere pornite: `prometheus`, `alertmanager`, `grafana`, `cadvisor`, `node-exporter`, `postgres-exporter`, `redis-exporter`

---

## 4. Variabilele de mediu

Copiezi **tot** blocul de mai jos în câmpul Environment Variables din Dockploy și **înlocuiești** valorile marcate cu `<...>`:

```env
# =============================================
# BAZA DE DATE
# =============================================
POSTGRES_PASSWORD=<parola_puternica_minim_20_caractere>

# =============================================
# DJANGO — SECURITATE
# =============================================
SECRET_KEY=<sir_aleatoriu_minim_50_caractere>
# Generezi cu: python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# =============================================
# DJANGO — CONFIGURARE DOMENIU
# =============================================
PUBLIC_PATH_PREFIX=
ADMIN_SITE_URL=https://www.doisense.eu
FRONTEND_BASE_URL=https://www.doisense.eu
ALLOWED_HOSTS=doisense.eu,backend
CORS_ALLOWED_ORIGINS=https://www.doisense.eu,https://doisense.eu
CSRF_TRUSTED_ORIGINS=https://www.doisense.eu,https://doisense.eu

# =============================================
# FRONTEND
# =============================================
NUXT_PUBLIC_SITE_URL=https://www.doisense.eu
NUXT_PUBLIC_APP_BASE_URL=/
NUXT_PUBLIC_API_BASE=https://www.doisense.eu/api
FRONTEND_HEALTHCHECK_PATH=/

# =============================================
# TRAEFIK — RUTARE
# =============================================
TRAEFIK_NETWORK=traefik
TRAEFIK_HOST=www.doisense.eu
TRAEFIK_WEB_RULE=Host(`www.doisense.eu`)||Host(`doisense.eu`)
TRAEFIK_API_RULE=(Host(`www.doisense.eu`)||Host(`doisense.eu`))&&PathPrefix(`/api`)
TRAEFIK_ADMIN_RULE=(Host(`www.doisense.eu`)||Host(`doisense.eu`))&&(PathPrefix(`/admin`)||PathPrefix(`/ro/admin`))
TRAEFIK_MEDIA_RULE=(Host(`www.doisense.eu`)||Host(`doisense.eu`))&&PathPrefix(`/media`)
TRAEFIK_API_STRIP_PREFIXES=/api
APP_INTERNAL_NETWORK=doisense_app_internal
BACKUP_INTERNAL_NETWORK=doisense_backup_internal

# =============================================
# MINIO — BACKUP INTERN
# =============================================
MINIO_ROOT_USER=doisense-backup
MINIO_ROOT_PASSWORD=<parola_puternica_minio>
MINIO_BACKUP_BUCKET=doisense-backup

# =============================================
# STRIPE — copiezi din dashboard stripe.com
# =============================================
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRODUCT_ID_BASIC=prod_U8ppJy3SiAJ81O
STRIPE_PRODUCT_ID_PREMIUM=prod_U8ppmA9p4nNZPx
STRIPE_PRODUCT_ID_VIP=prod_U8pp6xlcmH60m9
STRIPE_PRICE_ID_PREMIUM=price_...

# =============================================
# AI — copiezi din conturile respective
# =============================================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# =============================================
# LOGIN SOCIAL (lași gol dacă nu e configurat)
# =============================================
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
NUXT_PUBLIC_GOOGLE_CLIENT_ID=
APPLE_CLIENT_ID=
NUXT_PUBLIC_APPLE_CLIENT_ID=
NUXT_PUBLIC_APPLE_REDIRECT_URI=

# =============================================
# GRAFANA
# =============================================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<parola_puternica_grafana>
```

> **Regula de aur**: `PUBLIC_PATH_PREFIX=` trebuie să fie **gol** (fără nimic după `=`).
> Asta face diferența față de dev unde era `/doisense`.

---

## 5. Comenzi obligatorii după primul Deploy

Fără acești pași, aplicația pornește dar **nu funcționează** (baza de date este goală).

### Cum deschizi consola unui container în Dockploy

Dockploy → proiect `doisense-production` → serviciu `doisense-app` → containerul **`backend`** → butonul **Terminal** (sau **Console**)

Se deschide un terminal direct în container, în browser.

---

### 5.1 Creează tabelele în baza de date

**Container**: `backend`

```bash
python manage.py migrate
```

Vei vedea linii de tipul:
```
Applying auth.0001_initial... OK
Applying users.0001_initial... OK
...
```

Dacă apare orice eroare roșie, oprești și trimiți eroarea pentru diagnosticare.

---

### 5.2 Colectare fișiere statice (Admin CSS/JS)

**Container**: `backend`

```bash
python manage.py collectstatic --no-input
```

Copiază fișierele de stil ale panoului de administrare. Fără asta, admin-ul arată stricat (doar text, fără design).

---

### 5.3 Creare cont administrator

**Container**: `backend`

```bash
python manage.py createsuperuser
```

Te va întreba:
- **Username**: alegi ce vrei (ex: `admin`)
- **Email**: adresa ta
- **Password**: o parolă puternică (nu se vede pe ecran când tastezi)
- **Password (again)**: confirmi

**Notează-le într-un loc sigur** — cu ele intri la `https://www.doisense.eu/ro/admin/`

---

### 5.4 (Opțional) Verificare baza de date

**Container**: `db`

```bash
psql -U doisense -d doisense -c "\dt"
```

Afișează lista de tabele create. Ar trebui să vezi zeci de tabele (users, profiles, payments etc.).

---

## 6. Verificare

Testezi în ordine, în browser:

| Ce verifici | URL | Ce trebuie să apară |
|---|---|---|
| Frontend | `https://www.doisense.eu` | Pagina principală a aplicației |
| API health | `https://www.doisense.eu/api/health` | `{"status": "ok", ...}` |
| Admin login | `https://www.doisense.eu/ro/admin/` | Pagina de login Django (cu design) |
| Admin acces | Te loghezi cu contul creat la pasul 5.3 | Dashboard admin |

Dacă toate funcționează → producția este online.

---

## 7. GitHub Actions — Environments și Secrets

Pentru ca deploy-ul automat să funcționeze (la push pe branch `prod`), trebuie configurate în GitHub.

### 7.1 Creare environments

GitHub → repo `doimih/doisense` → **Settings** → **Environments** → **New environment**:
- Creezi `development`
- Creezi `production`

### 7.2 Secrets pentru fiecare environment

Pentru **fiecare** environment (development și production separat), adaugi:

| Secret | Valoare |
|---|---|
| `DEPLOY_HOST` | IP-ul sau hostname-ul serverului |
| `DEPLOY_USER` | Utilizatorul SSH (ex: `root` sau `deploy`) |
| `DEPLOY_SSH_KEY` | Cheia privată SSH (conținutul fișierului `~/.ssh/id_rsa`) |
| `DEPLOY_PATH` | Calea pe server unde este codul (ex: `/home/deploy/doisense`) |

### 7.3 Cum funcționează după configurare

- Push pe branch `main` → declanșează **CD Development** → deploy pe serverul de dev
- Push pe branch `prod` → declanșează **CD Production** → deploy pe serverul de producție (cu gate check că CI a trecut)

---

## Rezumat în 10 pași

```
1.  Domeniul doisense.eu → A record îndreptat spre IP server
2.  Dockploy instalat pe server
3.  Dockploy → Create Project: doisense-production
4.  Creare volum: doisense_pgdata
5.  Creare volum: doisense_media
6.  Creare volum: doisense_backup_data
7.  Creare volum: prometheus_data
8.  Creare volum: grafana_data
9.  Creare serviciu Docker Compose → docker-compose.yml (branch: prod) → adaugi env din Secțiunea 4 → Deploy
10. Din consola containerului backend:
      python manage.py migrate
      python manage.py collectstatic --no-input
      python manage.py createsuperuser
11. Creare serviciu Docker Compose → docker-compose.monitoring.yml (branch: prod) → Deploy
12. Verifici https://www.doisense.eu
```
