# Security Hardening Implemented

Date: 2026-03-12
Scope: Application security + API abuse protection + container/network hardening

## 1) Django Security Hardening

Implemented in backend settings:

- Restricted default `ALLOWED_HOSTS` (removed wildcard fallback behavior).
- Added production guard:
  - app fails fast when `DEBUG=False` and `SECRET_KEY` is left default.
- Enabled DRF throttling stack globally:
  - `AnonRateThrottle`
  - `UserRateThrottle`
  - `ScopedRateThrottle`
- Added detailed scope rates for:
  - `health`
  - `search`
  - `geo`
  - `analytics_track`
  - `contact_config`
  - `contact_submit`
  - `auth_register`
  - `auth_activate`
  - `auth_login`
  - `auth_refresh`
  - `auth_social`
  - `auth_recover`
  - `auth_reset_confirm`
- Enforced secure proxy/SSL behavior:
  - `USE_X_FORWARDED_HOST`
  - `SECURE_PROXY_SSL_HEADER`
  - `SECURE_SSL_REDIRECT`
- Hardened session and CSRF cookies:
  - `SESSION_COOKIE_SECURE`
  - `SESSION_COOKIE_HTTPONLY`
  - `SESSION_COOKIE_SAMESITE`
  - `CSRF_COOKIE_SECURE`
  - `CSRF_COOKIE_HTTPONLY`
  - `CSRF_COOKIE_SAMESITE`
- Enabled browser- and transport-level hardening:
  - `SECURE_HSTS_SECONDS`
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS`
  - `SECURE_HSTS_PRELOAD`
  - `SECURE_CONTENT_TYPE_NOSNIFF`
  - `SECURE_REFERRER_POLICY`
  - `SECURE_CROSS_ORIGIN_OPENER_POLICY`
  - `X_FRAME_OPTIONS=DENY`
- Added upload/request memory caps:
  - `DATA_UPLOAD_MAX_MEMORY_SIZE`
  - `FILE_UPLOAD_MAX_MEMORY_SIZE`
- Set `CORS_ALLOW_CREDENTIALS=False`.

File:
- `backend/config/settings.py`

## 2) Public Endpoint Abuse Protection (`core`)

Implemented in core API views:

- Added scoped throttling to public (`AllowAny`) endpoints:
  - health
  - cms public/preview/menu
  - geo language
  - search
  - analytics track
  - contact config
  - contact submit
- Added analytics payload guard:
  - reject oversized `properties` JSON payload (storage abuse protection).
- Added contact form input size limits:
  - full name length limit
  - subject length limit
  - message length limit

File:
- `backend/core/views.py`

## 3) Auth Endpoint Hardening (`users`)

Implemented in auth/account views:

- Added scoped throttling to:
  - register
  - activate
  - login
  - refresh
  - social login
  - password recovery request
  - password reset confirm
- Strengthened password reset confirm flow:
  - validates new password with Django password validators before save
  - returns controlled validation error response on failure

File:
- `backend/users/views.py`

## 4) Container Networking Isolation (App Stack)

Implemented in main compose:

- Removed host port publishing (`ports`) and retained only internal `expose`.
- Added dedicated internal Docker network:
  - `app_internal` with `internal: true`
- Attached app services to internal network:
  - `db`, `redis`, `backend`, `frontend`
- Kept only required Traefik connectivity for externally routed services:
  - `backend` and `frontend` also connected to `traefik` network

File:
- `docker-compose.yml`

## 5) Container Networking Isolation (Monitoring Stack)

Implemented in monitoring compose:

- Removed all host port publishing (`ports`) for monitoring services.
- Kept service communication internal-only using `expose`.
- Added dedicated internal Docker network:
  - `monitoring_internal` with `internal: true`
- Attached monitoring services to internal network:
  - prometheus
  - alertmanager
  - grafana
  - cadvisor
  - node-exporter
  - postgres-exporter
  - redis-exporter

File:
- `docker-compose.monitoring.yml`

## 6) Compose Credential Hardening

Implemented in compose runtime configuration:

- Replaced weak hardcoded DB password usage with env-driven password references.
- Updated backend `DATABASE_URL` to consume `POSTGRES_PASSWORD` env variable.
- Hardened Grafana admin password fallback value.
- Updated postgres-exporter DSN to use env password reference.

Files:
- `docker-compose.yml`
- `docker-compose.monitoring.yml`

## 7) Current Container Security Audit Status

After changes, these are true:

- External direct host port exposure from project compose files is removed.
- Container-to-container communication is internalized via Docker internal networks.
- External traffic path is controlled through Traefik (single ingress model).

Residual risks still noted (not yet patched in this pass):

- Containers generally run as root by default (no explicit non-root user in Dockerfiles).
- Missing runtime hardening flags in compose for many services:
  - `cap_drop`
  - `security_opt: no-new-privileges:true`
  - `read_only`
  - `tmpfs`
  - `pids_limit`
- cAdvisor has high-privilege host mounts (`/`, `/var/run`, `/var/lib/docker`).
- WAL-G binary download in DB image build has no checksum/signature verification.
- Base images are tag-pinned, not digest-pinned.

## 8) Recommended Next Hardening Batch

1. Run services as non-root where feasible (`USER` in Dockerfiles + compose `user`).
2. Add compose runtime restrictions (`cap_drop`, `no-new-privileges`, `read_only`, `tmpfs`, `pids_limit`).
3. Move cAdvisor behind an optional profile and only enable when required.
4. Add WAL-G artifact checksum verification during image build.
5. Pin base images by digest for deterministic, safer rebuilds.

---

Prepared for VPS staging before production migration week.
