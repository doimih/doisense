# Depanare 404 – Doisense nu se vede pe internet

Dacă **https://projects.doimih.net/doisense** dă 404, verifică pe server următoarele.

---

## 1. Traefik trebuie să vadă containerele (network)

Traefik citește labels de pe containere **doar dacă sunt pe un network la care Traefik este conectat**.

- **În acest proiect:** `frontend` și `backend` sunt pe network-ul extern `traefik`.
- Pe server, network-ul poate avea alt nume (ex. `traefik_default`, `proxy`).

**Ce să faci:**

1. Află cum se numește network-ul Traefik:
   ```bash
   docker network ls | grep -i traefik
   # sau
   docker network ls
   ```
2. Dacă Traefik rulează tot în Docker, de obicei există un network de tip `traefik_default` sau similar. **Actualizează** în `docker-compose.yml` la final:
   ```yaml
   networks:
     traefik:
       external: true
   ```
   și schimbă numele `traefik` în numele real (ex. `traefik_default`), sau creează network-ul:
   ```bash
   docker network create traefik
   ```
3. Repornește stack-ul Doisense:
   ```bash
   cd /path/to/doisense
   docker compose down
   docker compose up -d --build
   ```

---

## 2. Entrypoint-ul Traefik (HTTPS)

Labels folosesc `entrypoints=websecure`. Dacă pe server Traefik are alt nume pentru HTTPS (ex. `web` sau `https`), rutele nu se leagă.

**Verificare:** în configurația Traefik (file sau labels), vezi cum se numește entrypoint-ul pentru portul 443. Setează în labels același nume, de ex.:
```yaml
- "traefik.http.routers.doisense-web.entrypoints=websecure"
# schimbă în ce folosești, ex. "https" sau "web"
```

---

## 3. Containerele rulează

```bash
docker compose ps
```

Trebuie să vezi `frontend` și `backend` cu status **Up**. Dacă unul e Exit, vezi loguri:
```bash
docker compose logs frontend
docker compose logs backend
```

---

## 4. Test direct pe server (fără Traefik)

Să excluzi problema Traefik:

```bash
# Frontend pe port 3000
curl -I http://localhost:3000/doisense/

# Backend pe port 8000
curl -I http://localhost:8000/api/
```

Dacă aici primești 200, dar în browser 404, problema e la **Traefik** (network sau entrypoint).

---

## 5. Traefik vede rutele?

Dacă ai dashboard Traefik activat, verifică dacă apar **doisense-web** și **doisense-api** în HTTP Routers.

Sau din linie de comandă (dacă ai `curl` pe server):
```bash
# Înlocuiește cu URL-ul tău Traefik API, dacă e activat
curl -s http://localhost:8080/api/http/routers | grep doisense
```

---

## Rezumat rapid

| Verificare              | Comandă / acțiune |
|-------------------------|--------------------|
| Network comun cu Traefik| `docker network ls` → folosește același nume în `docker-compose.yml` |
| Entrypoint HTTPS        | Potrivește `entrypoints=websecure` cu config Traefik |
| Containere Up           | `docker compose ps` și `docker compose logs` |
| Test fără Traefik       | `curl http://localhost:3000/doisense/` și `curl http://localhost:8000/api/` |

După ce corectezi network-ul și eventual entrypoint-ul, repornește `docker compose up -d` și reîncearcă **https://projects.doimih.net/doisense**.

---

## 6. Eroare la "Send test email" in admin

Daca vezi mesajul:

`EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive`

inseamna ca in `System Configuration -> Contact & Email` sunt bifate ambele optiuni SMTP.

### Solutie

Activeaza doar una dintre ele:

- port `587`: `TLS=true`, `SSL=false`
- port `465`: `TLS=false`, `SSL=true`

Salveaza configurarea si ruleaza din nou butonul `Send test email`.
