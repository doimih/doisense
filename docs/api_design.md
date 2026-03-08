# Reguli de design API – Doisense

## 1. Bază

- REST over HTTP/HTTPS.
- JSON pentru request/response.
- Prefix: `/api/` (în producție: `https://projects.doimih.net/doisense/api`).

## 2. Autentificare

- JWT: access token (scurt) + refresh token.
- Header: `Authorization: Bearer <access_token>` sau cookie (configurabil).
- Endpoints:
  - `POST /api/auth/register` – body: email, password, language?
  - `POST /api/auth/login` – body: email, password
  - `POST /api/auth/refresh` – body: refresh (sau cookie)

## 3. Convenții

- GET: listă sau detaliu (query params pentru filtre).
- POST: creare (body JSON).
- PATCH: actualizare parțială (body JSON).
- Coduri HTTP: 200, 201, 400, 401, 403, 404, 429, 500.
- Erori: `{ "detail": "..." }` sau `{ "field": ["error"] }`.

## 4. Endpoints principale

| Metodă | Path | Descriere |
|--------|------|-----------|
| POST | /api/auth/register | Înregistrare |
| POST | /api/auth/login | Login |
| POST | /api/auth/refresh | Refresh token |
| GET | /api/profile | Profil curent (auth) |
| PATCH | /api/profile | Actualizare profil (auth) |
| POST | /api/chat/send | Trimite mesaj chat (auth, rate limit) |
| GET | /api/journal/questions | Întrebări jurnal (query: language) |
| POST | /api/journal/entries | Creare entry (auth) |
| GET | /api/programs | Listă programe (auth, premium filtrat) |
| GET | /api/programs/{id}/days/{n} | Conținut zi (auth, premium check) |
| POST | /api/payments/create-checkout-session | Stripe Checkout URL (auth) |
| POST | /api/payments/webhook | Webhook Stripe (semnătură) |

## 5. Versionare

- Pentru moment fără versionare în URL (/api/v1/). Dacă se introduce mai târziu, se păstrează backward compatibility.

## 6. Exemple

### Register
```http
POST /api/auth/register
Content-Type: application/json

{ "email": "user@example.com", "password": "SecurePass123", "language": "ro" }
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{ "email": "user@example.com", "password": "SecurePass123" }
```

### Chat send
```http
POST /api/chat/send
Authorization: Bearer <token>
Content-Type: application/json

{ "message": "Cum mă simt azi?" }
```

### Journal entry
```http
POST /api/journal/entries
Authorization: Bearer <token>
Content-Type: application/json

{ "question_id": 1, "content": "Mă simt liniștit.", "emotions": ["calm", "hopeful"] }
```
