# Doisense Security Executive Summary

Date: 2026-03-30  
Version: 1.0  
Audience: client leadership, procurement, delivery managers

## Business-Level Security Position

Doisense is secured using a layered defense approach across infrastructure, application, authentication, backup, and monitoring.

In practical terms, this means:
- public exposure is minimized,
- sensitive authentication data is better protected,
- backup and recovery controls are in place,
- continuous monitoring supports fast operational response.

Current status: production-ready with standard operational governance (secret rotation, patching cadence, and incident response discipline).

## What Was Hardened

### 1) Network and Exposure
- Core services are not directly exposed as public host ports.
- Traffic is routed through ingress, while internal traffic remains on Docker internal networks.
- Data and backup paths are segmented from edge-facing routes.

Business impact:
- Lower external attack surface and better containment.

### 2) Runtime Container Security
- No-new-privileges and capability drops are used broadly.
- Process limits are applied to reduce abuse potential.
- Writable runtime surfaces are reduced where feasible.

Business impact:
- Reduced blast radius if a component is compromised.

### 3) Application Security Controls (Backend)
- HTTPS enforcement and proxy-aware secure settings enabled.
- HSTS enabled for stronger transport guarantees.
- Secure cookie controls enabled.
- Auth endpoints protected with throttling to limit abuse.

Business impact:
- Better resilience to interception, downgrade, and brute-force behavior.

### 4) Authentication Security Upgrade
- Migration from browser localStorage token persistence to HttpOnly cookie-based JWT handling.
- Server-side login, refresh, and logout now manage auth cookies directly.
- Refresh flow supports secure browser session continuity.

Business impact:
- Significant reduction in token theft risk via frontend script exposure.

### 5) Backup and Recovery Security
- Internal object storage added for backups in the private network plane.
- Backup tooling integrity check (SHA256) added in build process.
- Backup and verification workflows validated.

Business impact:
- Stronger recoverability and reduced backup tampering risk.

### 6) Monitoring and Operational Visibility
- Monitoring stack runs with hardened runtime settings.
- Metrics and alerting are active for key components.
- Configuration stabilized for reliable observability runtime.

Business impact:
- Faster detection and response to incidents.

## Validation Snapshot

The following validations were completed:
- infrastructure and compose configuration checks,
- backend framework checks,
- frontend production build,
- authentication tests for cookie lifecycle,
- user-domain regression tests,
- backup create and verification tests.

Result summary:
- Auth API tests: passed.
- Users suite: passed.
- Backend checks: passed.
- Frontend build: passed.

## Residual Risk and Ongoing Responsibilities

Security is a continuous process. Ongoing controls required:
- rotate all secrets and remove placeholders before go-live,
- patch base images and dependencies regularly,
- enforce alert response and escalation discipline,
- run periodic restore drills,
- review privileges and access on a recurring cycle.

## Go-Live Recommendation

Go-live is supported from a security posture perspective, provided that:
- production secrets are fully rotated,
- TLS and ingress policies are confirmed,
- restore drill is successfully executed,
- operations team confirms alerting ownership and response SLAs.

## Linked Detailed Report

For full technical detail and control rationale, see:
- security.md
