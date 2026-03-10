# Wagtail Implementation Plan (Phased)

Date: 2026-03-10
Target: integrate Wagtail for non-technical editors without disrupting current platform.

## Phase 0 - Decision Lock

1. Approve page ownership map:
- Wagtail-managed pages
- Legacy `CMSPage`-managed pages

2. Approve target URL namespaces:
- Wagtail admin: `/doisense/wagtail/admin/`
- Wagtail docs/media: `/doisense/wagtail/documents/` (if enabled)

3. Define migration pilot scope (recommended):
- `home`, `features`, `pricing`, `about`, `contact`

## Phase 1 - Technical Bootstrap

1. Add Wagtail dependencies compatible with current Django/Python baseline.
2. Add Wagtail apps in Django settings in a controlled order.
3. Add Wagtail URLs under dedicated namespace (no replacement of current admin).
4. Run migrations in staging only.

Exit criteria:

- `manage.py check` clean
- Wagtail admin loads
- no regression in existing `/doisense/ro/admin/`

## Phase 2 - Content Models and Editorial UX

1. Create Wagtail page models for marketing pages.
2. Add StreamField blocks matching frontend component library.
3. Add SEO fields and publish workflow defaults.
4. Configure editor roles and permissions.

Exit criteria:

- editors can create/update/publish pilot pages without developer support

## Phase 3 - Frontend Delivery Integration (Nuxt)

1. Choose delivery mode:
- headless API consumption from Nuxt (recommended), or
- server-side page rendering from Django for selected routes

2. Implement one mode only for pilot pages.
3. Add preview flow for editorial QA.

Exit criteria:

- pilot pages render correctly in Nuxt for all enabled locales

## Phase 4 - Controlled Migration

1. Migrate pilot content from `CMSPage` to Wagtail.
2. Freeze legacy edits for migrated slugs.
3. Add monitoring and rollback plan.

Exit criteria:

- production pilot stable for 2 release cycles

## Phase 5 - Expand or Stop

1. If KPIs improve, migrate remaining page families.
2. If KPIs do not improve, keep Wagtail only for selected page types.

## KPI Set for Go/No-Go

1. Editor time to publish page.
2. Number of developer interventions per week.
3. Content defect rate after publish.
4. i18n consistency across locales.

## Risk Register

1. Dual CMS ownership conflict.
Mitigation: ownership map and edit freeze by slug.

2. URL conflicts with existing admin.
Mitigation: strict namespace separation.

3. Multilingual model mismatch.
Mitigation: pilot locale strategy before full rollout.

4. Editor retraining burden.
Mitigation: template-first rollout + short onboarding sessions.

## Immediate Next Actions

1. Approve Phase 0 decisions.
2. Execute Phase 1 in staging branch only.
3. Run full regression suite before any production toggle.
