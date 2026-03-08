# Reguli de cod și convenții – Doisense

## 1. Backend (Django / Python)

- **Python**: 3.11+
- **Stil**: Black (formatare), Ruff (lint). Linie max ~100 caractere.
- **Imports**: ordonate (stdlib, third-party, local), una per linie pentru third-party/local.
- **Apps**: un responsabilitate principală per app. Modele în `models.py`, validări în serializers, logică business în services dacă e cazul.
- **API**: DRF – ViewSet sau APIView, serializers pentru input/output, permission classes (IsAuthenticated etc.).
- **Secrets**: niciodată în cod; variabile de mediu (os.environ / django.conf.settings).
- **Teste**: pytest + pytest-django. Naming: `test_<action>_<context>`. Mock pentru Stripe și AI.

## 2. Frontend (Nuxt 3 / TypeScript)

- **TypeScript**: strict. Interfețe pentru API responses și props.
- **Componente**: compoziție API (script setup). Props și emit tipizate.
- **Stil**: Tailwind. Clase consistente; evitat stil inline pentru logică complexă.
- **i18n**: toate textele UI în locale (ro, en, de, it, es, pl). Key-uri: `section.key` (ex: `auth.login`).
- **API**: `$fetch` sau `useFetch` cu baseURL din runtimeConfig (`/doisense` + `/api` proxy sau direct).
- **Store (Pinia)**: state minimal; date volatile din API prin composables dacă e cazul.
- **Teste**: Jest. Componente cu mount, store-uri și composables unit testate. Acoperire țintă ≥80%.

## 3. Git / branch-uri

- `main` – production-ready.
- Feature branches: `feature/nume` sau `fix/nume`. PR cu code review (inclusiv AI).

## 4. Docker

- Imagini clare: un proces principal per container.
- Variabile de mediu pentru config (DB, Redis, Stripe, API keys). Nu secrets în Dockerfile.
- Traefik: doar labels pe serviciile acestui proiect; fără modificări la config-ul global Traefik.

## 5. Securitate

- Parole: hash cu algoritm sigur (Django default).
- JWT: expirare scurtă pentru access, refresh rotit.
- Input: validare mereu (serializers DRF, validare limbă, lungimi max).
- Rate limiting pe endpoint-uri sensibile (chat).

## 6. AI prompts (template-uri)

- Păstrate în repo sau DB (ai_conversationtemplate). Versionate; fără date personale în prompt-uri, doar placeholders.
