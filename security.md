# Doisense Security Overview

Document version: 1.0  
Date: 2026-03-30  
Audience: business stakeholders, operations teams, and technical reviewers

## 1. Executive Summary

Doisense has been hardened for production with a defense-in-depth approach across:
- container runtime isolation,
- internal network segmentation,
- secure authentication token handling,
- encrypted transport assumptions at ingress,
- backup integrity controls,
- observability and operational monitoring.

The current posture is suitable for production rollout with standard operational governance (secrets rotation, patch cadence, and alert handling discipline).

## 2. Scope and Architecture

This security posture covers the deployed stack in Docker:
- frontend (Nuxt),
- backend (Django/DRF),
- PostgreSQL,
- Redis,
- monitoring stack (Prometheus, Alertmanager, Grafana, exporters),
- internal backup storage (MinIO),
- Traefik ingress for external traffic.

Network model:
- public access is routed through Traefik,
- service-to-service traffic runs on internal Docker networks,
- database and backup traffic are isolated from edge exposure.

## 3. Security Controls Implemented

### 3.1 Network and Exposure Controls

Implemented controls:
- No direct host port publishing for core app services; internal service ports are exposed only to Docker networks.
- Database service is isolated from ingress-facing network paths.
- Dedicated internal network for backup data flow.

Security value:
- Reduces direct attack surface.
- Limits lateral movement opportunities.
- Keeps backup plane separated from web traffic plane.

### 3.2 Container Runtime Hardening

Implemented controls (where compatible):
- `no-new-privileges` enabled.
- Linux capabilities dropped (`cap_drop: ALL`) for multiple services.
- Process limits (`pids_limit`) applied.
- Read-only or tmpfs usage applied where practical for supporting components.

Security value:
- Restricts privilege escalation paths.
- Reduces blast radius from container compromise.
- Limits abuse of process spawning and writable filesystem surfaces.

### 3.3 Application Security (Django)

Implemented controls:
- `SECURE_SSL_REDIRECT` in production context.
- `SECURE_PROXY_SSL_HEADER` set for reverse proxy deployments.
- HSTS controls enabled (`SECURE_HSTS_SECONDS`, include subdomains, preload).
- Secure cookie settings enabled for session and CSRF cookies.
- Strict DRF throttle rates configured for auth-sensitive endpoints.

Security value:
- Enforces HTTPS behavior and improves transport integrity.
- Improves resistance to downgrade and cookie interception attacks.
- Reduces brute-force and endpoint abuse risk.

### 3.4 Authentication Hardening

Implemented controls:
- Migration from browser localStorage refresh-token model to HttpOnly cookie model for JWT lifecycle.
- Backend authentication class supports bearer header first, with secure cookie fallback.
- Login/social/session bridge endpoints set HttpOnly auth cookies.
- Refresh endpoint accepts refresh cookie and rotates access token response/cookie.
- Logout endpoint clears auth cookies server-side.

Security value:
- Reduces token exfiltration risk from frontend XSS vectors compared to localStorage persistence.
- Centralizes token lifecycle controls server-side.
- Supports safer browser session continuity.

### 3.5 Backup and Data Protection Controls

Implemented controls:
- Internal MinIO S3-compatible backup target integrated in Docker network.
- Idempotent bucket bootstrap (`minio-init`) during stack startup.
- WAL-G binary integrity check with SHA256 in DB image build.
- Backup and verify scripts operational against internal object storage.

Security value:
- Keeps backup traffic/storage internal to deployment boundary.
- Adds supply-chain integrity verification for critical backup tooling.
- Improves recoverability assurance through verification workflows.

### 3.6 Monitoring and Detection Readiness

Implemented controls:
- Prometheus, Alertmanager, Grafana stack running with hardened runtime options.
- Exporters connected to internal service network for observability coverage.
- Alertmanager configuration stabilized for reliable startup.

Security value:
- Enables early anomaly and health detection.
- Supports operational incident response with measurable telemetry.

## 4. Validation and Evidence

Validation actions performed:
- Docker Compose configuration validation.
- Service health checks across app and monitoring stack.
- Backend framework checks (`manage.py check`).
- Frontend production build verification.
- Authentication test suite updates and execution for cookie-based flow.
- Users domain regression tests executed in container runtime.
- Backup create/verify workflow executed against internal MinIO target.

Recent auth test status:
- Auth API tests: passed (including cookie flow coverage).
- Users test suite: passed.

## 5. Residual Risks and Operational Responsibilities

No production system is risk-free. Residual risks and required controls include:
- Secret hygiene: all default/example values must be replaced before production.
- Patch management: base images and dependencies must be updated on a regular cycle.
- Alert response: alerting only helps if on-call response procedures are enforced.
- Access governance: administrative credentials should be least-privilege and rotated.
- Backup governance: periodic restore drills are mandatory, not optional.

## 6. Customer-Facing Security Positioning

Recommended customer-facing statement:
- The platform uses layered controls at infrastructure, runtime, and application levels.
- Sensitive authentication tokens are protected with HttpOnly cookie handling to reduce browser-side theft risk.
- Core data services are isolated behind internal networking and are not directly exposed to the public edge.
- Recovery readiness is backed by internal object-storage backups with integrity checks and verification routines.
- Continuous observability is in place to detect failures and support rapid incident handling.

## 7. Go-Live Checklist

Pre-go-live mandatory checks:
- Replace all placeholder credentials and rotate secrets.
- Confirm TLS certificates and Traefik routing policies.
- Confirm HSTS and secure-cookie behavior in production domain.
- Verify backup success and perform a test restore in non-production.
- Confirm alert receivers and escalation contacts are active.
- Re-run smoke tests after final image/tag lock.

Post-go-live recurring checks:
- Daily: backup success and alert queue review.
- Weekly: vulnerability and dependency updates review.
- Monthly: restore drill and access review.
- Quarterly: full security posture review and hardening backlog refresh.

## 8. File-Level Security References

Primary implementation references:
- `docker-compose.yml`
- `docker-compose.monitoring.yml`
- `docker/db/Dockerfile`
- `backend/config/settings.py`
- `backend/users/authentication.py`
- `backend/users/views.py`
- `backend/users/urls.py`
- `backend/users/tests/test_auth_api.py`
- `docs/DISASTER_RECOVERY.md`

---

If needed for procurement/compliance reviews, this document can be extended with:
- control-to-standard mapping (ISO 27001 / SOC 2 style),
- RACI ownership matrix,
- incident severity taxonomy and SLA table,
- formal change log and approval signatures.
