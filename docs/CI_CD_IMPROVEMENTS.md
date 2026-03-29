# CI/CD Pipeline - Improvements & Documentation

## Overview

This document outlines all the security and reliability improvements made to the CI/CD pipeline as of March 2026.

## Implemented Improvements

### 1. ✅ GitHub Actions Pinning

**Why**: Prevent malicious action updates by pinning to specific patch-level versions.

**Changes Made**:
- All GitHub Actions pinned to specific patch versions (e.g., `@v4.1.7` instead of `@v4`)
- Workflows updated:
  - `.github/workflows/ci.yml` - 5 actions pinned
  - `.github/workflows/cd.yml` - 2 actions pinned
  - `.github/workflows/security.yml` - All actions pinned (new file)

**Files**:
- `.github/workflows/ci.yml` - Lines 34, 38, 48, 52, 56
- `.github/workflows/cd.yml` - Lines 7, 31

### 2. ✅ Dependency Security Scanning

**Why**: Detect known vulnerabilities in Python and Node.js dependencies automatically.

**New Workflow**: `.github/workflows/security.yml`

**Features**:
- **pip-audit**: Scans Python dependencies in `backend/requirements.txt`
- **npm-audit**: Scans npm/pnpm dependencies in `frontend/pnpm-lock.yaml`
- **Trivy**: Container image vulnerability scanning for both backend and frontend
- **CodeQL**: Semantic code analysis for Python and JavaScript
- **Truffelhog**: Secret leak detection

**Triggers**:
- Every push to main and pull requests
- Daily scheduled scan at 2 AM UTC

### 3. ✅ Dependabot Configuration

**Why**: Automate dependency updates with automated pull requests.

**New File**: `.github/dependabot.yml`

**Configured Updates**:
1. **Python dependencies** (weekly)
   - Scans `backend/requirements.txt`
   - Creates PRs for updates
   - Includes both production and dev dependencies

2. **NPM/pnpm dependencies** (weekly)
   - Scans `frontend/pnpm-lock.yaml`
   - Creates PRs for updates
   - Labels: `dependencies`, `javascript`

3. **GitHub Actions** (weekly)
   - Automatically updates action versions
   - Labels: `dependencies`, `github-actions`

4. **Docker base images** (weekly)
   - Updates `node:20-alpine`, `python:3.11-slim`, `postgres:15-alpine`
   - Labels: `dependencies`, `docker`

**Schedule**: Every Monday at 4 AM UTC
**PR Limit**: 5 for pip/npm, 3 for actions/docker

### 4. ✅ Build Reproducibility Fix

**Why**: Ensure frontend builds are consistent between CI and production.

**Problem**: CI used `npm` while Docker used both `npm` and `npm ci` conditionally

**Solution**:
- Updated `frontend/Dockerfile` to explicitly use `pnpm`
- Pinned pnpm to version 9 globally
- Removed npm fallback logic
- Uses `pnpm install --frozen-lockfile` for deterministic builds

**Files Changed**:
- `frontend/Dockerfile` - Lines 4-6

### 5. ✅ Production Parity in CI Testing

**Why**: SQLite and PostgreSQL have different behaviors; bugs can hide in CI but appear in production.

**Changes**:
- Migrated backend CI from SQLite to PostgreSQL 15-alpine
- Added Redis service to CI for cache testing
- Added health checks for both services
- Ensures test database matches production schema/behavior

**CI Services** (`.github/workflows/ci.yml`):
```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_USER: doisense
      POSTGRES_PASSWORD: ci-db-password
      POSTGRES_DB: doisense_test
  redis:
    image: redis:7-alpine
```

### 6. ✅ Container Restart Policies

**Why**: When a container crashes, it should automatically restart (unless intentionally stopped).

**Changes to `docker-compose.yml`**:
- Added `restart: unless-stopped` to all 4 services:
  - `db` (PostgreSQL)
  - `redis`
  - `backend` (Django)
  - `frontend` (Nuxt)

- Added `start_period` to health checks:
  - `db`: 10 seconds
  - `redis`: 10 seconds
  - `backend`: 15 seconds (health check slower)
  - `frontend`: 15 seconds (health check slower)

**Healthcare Checks**:
- `db`: `pg_isready -U doisense`
- `redis`: `redis-cli ping`
- `backend`: curl to `/api/health/` endpoint
- `frontend`: wget to `/doisense/` homepage

### 7. ✅ Post-Deploy Health Verification

**Why**: Ensure deployed services are actually healthy before marking deployment as successful.

**Changes to `.github/workflows/cd.yml`**:
After `rebuild_all.sh`, the workflow now:
1. Waits up to 30 attempts for backend API to be healthy
2. Waits for frontend homepage to respond
3. Waits for database to accept connections
4. Verifies all three services simultaneously
5. **Fails deployment if services don't become healthy**
6. Shows `docker compose ps` output on failure for debugging

**Checks**:
- Backend: `curl -f http://localhost:8000/api/health/`
- Frontend: `curl -f http://localhost:3000/doisense/`
- Database: `docker compose exec -T db pg_isready`

### 8. ✅ Coverage Thresholds Improved

**Frontend Tests** (`frontend/jest.config.js`):
- Global threshold increased from 50% to:
  - **Branches**: 60%
  - **Functions**: 65%
  - **Lines**: 65%
  - **Statements**: 65%

- Per-directory thresholds:
  - `./components/`: 50-60% (UI components are harder to test)
  - `./stores/`: 70-80% (state logic should be well-tested)

**Backend Tests** (`backend/pytest.ini`):
- Added coverage collection to pytest runs
- Threshold: **75% overall** (fail-ci-if-error)
- Generates HTML and XML reports
- Excludes migrations, tests, and boilerplate

### 9. ✅ Coverage Reporting to Codecov

**CI/CD Integration**:
- Backend coverage uploaded from `backend/coverage.xml`
- Frontend coverage uploaded from `frontend/coverage/cobertura-coverage.xml`
- Uses `codecov/codecov-action@v3.1.5`
- Reports accessible in repository settings

**Command Changes**:
- Backend: `pytest --cov --cov-report=xml`
- Frontend: `pnpm run test -- --runInBand --coverage --coverageReporters=cobertura`

---

## Workflow Triggers

### CI Workflow (`.github/workflows/ci.yml`)
- **On**: Pull requests to main, pushes to main
- **Duration**: ~12-15 minutes per run
- **Artifacts**: Coverage reports, test results
- **Concurrent**: Limited by concurrency group (latest run only)

### CD Workflow (`.github/workflows/cd.yml`)
- **On**: Manual trigger (`workflow_dispatch`)
- **Inputs**:
  - `ref`: Git reference to deploy (branch, tag, commit SHA)
  - `run_migrations`: Boolean to run Django migrations
- **Duration**: ~5-10 minutes
- **Post-Deploy**: Health checks included

### Security Workflow (`.github/workflows/security.yml`)
- **On**: Pushes to main, PRs to main, daily at 2 AM UTC
- **Duration**: ~10-12 minutes per run
- **Reports**: Uploaded to GitHub Security tab as SARIF files
- **Strictness**: HIGH (fails on CRITICAL/HIGH severity)

---

## Maintenance Tasks

### Weekly
- Review Dependabot PRs for dependency updates
- Run integration tests locally before merging Dependabot PRs

### Monthly
- Review security scan results in GitHub Security tab
- Check Codecov trends for coverage regressions
- Review action version updates for breaking changes

### Quarterly
- Update base Docker images to latest LTS versions
- Audit and review all pinned action versions
- Review Python and Node.js version EOL status

---

## How to Add New Secrets for GitHub Actions

1. Go to **Settings → Secrets → Actions**
2. Click **New repository secret**
3. Add required secrets for CD workflow:
   - `DEPLOY_HOST`: Server hostname
   - `DEPLOY_USER`: SSH user
   - `DEPLOY_SSH_KEY`: Private SSH key
   - `DEPLOY_PATH`: Deploy directory on server

---

## How to Trigger Manual Deployment

1. Go to **Actions → CD**
2. Click **Run workflow**
3. Enter:
   - Git ref (e.g., `main`, `v1.2.3`, commit SHA)
   - Check "Run backend migrations" if needed
4. Click **Run workflow**
5. Monitor deployment in workflow logs

---

## Debugging Failed Workflows

### CI Failures
1. Check job logs: **Actions → CI → [Run number] → Logs**
2. Common issues:
   - Import errors → missing dependencies
   - Test failures → check database connection
   - Lint failures → run `black --check .` and `ruff check .` locally

### CD Failures
1. Check job logs for deployment step
2. Check post-deploy health checks:
   ```
   ERROR: Services failed to become healthy after deploy
   Current container status:
   # Shows docker compose ps output
   ```
3. SSH to server and check:
   ```bash
   docker compose logs backend
   docker compose logs frontend
   docker compose ps
   ```

### Security Scan Failures
1. Navigate to **Security → Code scanning alerts**
2. Review vulnerabilities found by Trivy, CodeQL, or pip-audit
3. For false positives, use `# nosec` comments in code

---

## Performance Baseline

- **CI Pipeline**: 12-15 minutes (parallel backend + frontend jobs)
- **CD Pipeline**: 5-10 minutes (build + deploy + health checks)
- **Security Scan**: 10-12 minutes (parallel dependency + container scans)
- **Codecov Upload**: <1 minute

---

## Security Hardening Checklist

- [x] All GitHub Actions pinned to patch versions
- [x] Automated dependency scanning (pip-audit, npm-audit)
- [x] Container vulnerability scanning (Trivy)
- [x] Code analysis (CodeQL)
- [x] Secret leak detection (Truffelhog)
- [x] Dependabot configured for auto-updates
- [x] Service restart policies enabled
- [x] Post-deploy health checks implemented
- [x] Coverage thresholds enforced
- [x] Production parity in CI (PostgreSQL instead of SQLite)

---

## Future Improvements (Optional)

1. **SLSA Provenance**: Sign build artifacts for supply-chain security
2. **Container Registry Scan**: Scan images in private registry before deployment
3. **E2E Testing**: Add Cypress/Playwright tests to CD workflow
4. **Performance Testing**: Add lighthouse/k6 performance benchmarks
5. **Database Migration Testing**: Pre-test migrations on staging before prod
6. **Rollback Automation**: Implement automatic rollback on deployment failure

---

**Last Updated**: March 29, 2026
**Maintained By**: Development Team
**Critical Issues**: Contact @doimih
