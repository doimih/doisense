# Wagtail Readiness Audit (Doisense)

Date: 2026-03-10
Scope: backend Django, admin architecture, CMS overlap risk, URL and i18n impact.

## Executive Summary

Status: Ready for phased Wagtail adoption.

Decision confidence: Medium-High.

Main reason: current stack is Django 5 + Python 3.11, which is compatible with current Wagtail release lines that support Django 5.x.

Primary caution: existing in-house CMS (`core.CMSPage` + custom admin UX) overlaps functionally with Wagtail pages, so migration strategy must avoid double source-of-truth.

## Audit Pass 1 (Runtime and Dependency Compatibility)

Evidence collected:

- Runtime Python in backend container: `3.11.14`
- Current backend dependency: `Django>=5.0,<6`
- System health: `python manage.py check` passes with no issues.

Compatibility conclusion:

- Backend runtime baseline is suitable for Wagtail introduction.
- No blocking runtime errors found in current deployment profile.

## Audit Pass 2 (Codebase Integration Risk)

### Existing CMS/Admin Surface

- Custom CMS model: `core.CMSPage`
- Custom admin UX with tabs and multilingual fields in `core/admin.py`
- Existing admin customization via `django-unfold`
- Existing rich text editor via `django-ckeditor-5`
- Newsletter admin and custom sidebar integrations already active

### URL Space and Routing

Current key URL prefixes:

- Admin: `/doisense/ro/admin/`
- API: `/api/*`
- Newsletter public: `/doisense/newsletter/*`

Risk note:

- Wagtail admin should be mounted on a non-conflicting prefix (recommended `/doisense/wagtail/admin/`), not over current Django admin path.
- Wagtail page serving should not be enabled globally until content source strategy is finalized.

### Content Source-of-Truth Risk

Main overlap zones:

- Marketing pages
- Legal pages
- Multilingual content variants

Risk note:

- Running both `CMSPage` and Wagtail as active editors for same pages creates editorial drift.
- Must define one owner per page type during transition.

## Final Readiness Verdict

Readiness: PASS with migration controls.

Required controls before implementation:

1. Define content ownership matrix (CMSPage vs Wagtail per page group).
2. Introduce Wagtail in a staged way (admin-only first, page serving later).
3. Keep current admin intact until Wagtail editors are trained and migration is validated.

## Suggested Adoption Guardrails

1. Use feature flag env var for Wagtail enablement in non-production first.
2. Keep current `/doisense/ro/admin/` unchanged.
3. Add Wagtail under separate menu entry and URL namespace.
4. Migrate one page family first (for example: marketing pages only).
5. Freeze edits in old source per migrated page to avoid data divergence.

## Double-Check Record

The audit was validated twice:

- Check 1: runtime/dependency compatibility and Django health check.
- Check 2: architecture and routing conflict scan against existing codebase.

Both checks indicate Wagtail can be adopted safely with staged rollout.
