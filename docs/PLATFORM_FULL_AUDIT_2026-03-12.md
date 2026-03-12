# Doisense Platform Full Audit

Date: 2026-03-12
Scope: CTO audit, Product audit, Growth audit
Status: Implemented review based on codebase state, validated live database snapshot, and recently deployed operational changes

## Executive Summary

Doisense has a solid product core and is operationally coherent for controlled rollout. The platform already covers the major building blocks expected from a modern guided wellbeing SaaS:

- structured onboarding with legal consent capture
- 7-day trial and feature gating by effective tier
- tier-differentiated AI behavior across Trial, Basic, Premium, and VIP
- manual VIP override with scheduled integrity audit
- early discount logic for first 500 users
- separate Support AI with ticket escalation
- admin-managed scheduler for recurring automation jobs
- GDPR deletion that removes personal data while preserving anonymized conversations

The current platform does not have structural product logic gaps. The main remaining work is maturity work: retention automation, persistent report objects, operational support workflow, backup restore controls, funnel analytics, and scaling discipline.

## Current Live Data Snapshot

Snapshot collected from the running backend database on 2026-03-12.

- Total users: 4
- Active users: 3
- Inactive users: 1
- Users by plan:
  - free: 2
  - trial: 2
  - basic: 0
  - premium: 0
  - vip: 0
- Premium-like users (`is_premium=true`): 2
- Manual VIP users: 0
- Early discount eligible users: 0
- Payments by status:
  - active: 0
  - cancelled: 0
  - past_due: 0
  - trialing: 0
- Support tickets total: 0
- Support tickets open/in progress: 0
- In-app notifications total: 0
- Notification deliveries total: 0
- Analytics events total: 0

Interpretation:

- the code paths are implemented, but the current live data set is too small to support statistically meaningful funnel or retention decisions
- growth and monetization work should proceed, but live dashboards will only become strategic after more traffic and events are collected

## 1. Complete List of Problems Detected

1. Reactivation automation is missing.
   - There is no dedicated win-back automation for churned or expired-paid users.

2. End-of-period downgrade communication is incomplete.
   - Cancel intent exists, but the post-cancellation communication path is weak and mostly webhook-driven.

3. Early-access pricing message is static in frontend.
   - The Premium pricing card shows the first-500 discount note in static UI copy rather than deriving it from real availability.

4. Backup scheduling is only partially unified.
   - App task scheduling is now admin-managed, but backup execution still runs via the dedicated DB-side WAL-G daemon.

5. Backup restore is not platform-administered.
   - Restore exists as an operational script, not as an audited platform workflow.

6. No autoscaling implementation exists.
   - Health checks and observability exist, but no orchestration logic scales services up or down.

7. Reports are more conversational than productized.
   - Premium/VIP reporting exists in AI behavior and prompts, but there is no explicit persistent reports domain model for long-term product UX.

8. Support workflow is still operationally shallow.
   - Ticket creation exists, but there is no SLA, owner assignment, internal note system, or escalation dashboard workflow.

9. Stripe is logically prepared but not operationally enabled in the current environment.
   - Current environment warnings confirm missing runtime Stripe credentials and webhook configuration.

10. Command naming can create operator confusion.
    - There are multiple `expire_trials` commands in different app namespaces.

11. Funnel tracking is not yet mature enough for growth analysis.
    - Analytics exist architecturally, but current event volume is too low and event coverage should be expanded for business visibility.

12. Churn analysis is conceptually possible but not yet operationally useful.
    - Dashboard signals exist, but no rich churn segmentation or reactivation orchestration is attached to them.

## 2. Complete List of Opportunities

1. Turn AI reports into persistent product artifacts.
   - Daily, weekly, and monthly reports could become first-class user-facing objects, especially for Premium and VIP.

2. Introduce win-back campaigns.
   - Separate flows for trial-expired, cancelled, and inactive users can materially improve retention.

3. Strengthen support operations.
   - Add assignment, priority, response target, and internal notes on tickets.

4. Make pricing promo state dynamic.
   - Frontend should reflect actual availability of first-500 discount eligibility.

5. Add cohort retention and conversion analytics.
   - Current architecture supports this direction, but product analytics needs deeper instrumentation.

6. Add proactive billing lifecycle messaging.
   - Expiration, failed payment, cancellation, and reactivation moments should be more visibly handled.

7. Add alerting.
   - Health endpoint, backup verification, and failed scheduled jobs should trigger operational notifications.

8. Expand in-app notifications.
   - Support, billing, milestone, and retention events can all use in-app notification surfaces.

9. Improve monetization architecture.
   - Annual plans, recovery offers, temporary grace logic, and pricing experiments can all increase conversion.

10. Deepen product continuity.
    - Better visible connections among journal, chat, plans, reports, and progress would improve retention and perceived value.

## 3. Complete List of Optimizations

1. Manual VIP logic was normalized.
   - Manual VIP now cleanly bypasses trial, discount application, and subscription interference.

2. Early discount logic was normalized.
   - Eligibility is derived from current business rules and no longer conflicts with manual VIP.

3. GDPR deletion logic was improved.
   - Deletion clears personal and derived state while preserving anonymized conversations.

4. Weekly manual VIP audit was added.
   - The audit now validates manual VIP integrity and can normalize stale discount flags.

5. Platform scheduler is admin-managed.
   - Scheduler jobs are now controlled from Django Admin instead of being hardcoded only in host cron.

6. Support AI can now create and reuse support tickets.
   - Escalated support requests are no longer conversational dead ends.

7. A health endpoint was added.
   - Basic database and cache readiness can now be checked reliably.

8. Admin navigation was improved.
   - Automation is now a dedicated section, grouping scheduler and backup controls.

9. Contact CTA and pricing UX were improved.
   - Contact button size was reduced and Premium pricing now surfaces the early-access value proposition.

10. Operational testing coverage improved.
    - New tests now validate scheduler behavior, health endpoint, support AI ticket creation, manual VIP audit, and billing logic.

## 4. Complete List of Necessary Implementations

1. Reactivation automation command and message design.
2. Dynamic pricing promo availability tied to backend state.
3. Persistent AI reports model and retrieval UX.
4. Support SLA workflow with owner assignment and admin notes.
5. Backup restore workflow with explicit operational logging.
6. Alerting around failed scheduled jobs, degraded health, and backup verification failure.
7. Funnel analytics expansion across landing, onboarding, trial, subscription, and churn.
8. Churn segmentation and reactivation paths.
9. Operator documentation for scheduler and backup interaction.
10. Long-term autoscaling and worker separation strategy.

## 5. Complete List of Logical Conflicts

1. Pricing UI shows first-500 messaging as static copy while actual eligibility is dynamic.

2. Scheduling is mostly unified, but backup execution still uses a separate DB-side daemon model.

3. Stripe readiness exists in logic, but runtime environment is not fully configured for live billing.

4. AI capability promises for reports and typology are stronger than the product's current persistence model.

5. Support AI escalation creates tickets, but support operations after ticket creation are still thin.

6. Dashboard logic can compute growth metrics, but current data volume is too small to support strategic interpretation.

## 6. Complete List of Validated Manual VIP Users

Result from live audit:

- none

Manual VIP audit output:

- manual_vip_count: 0
- detected_problems: none
- wrongly_marked_users: none
- detected_conflicts: none
- possible_missing_manual_vip_users: none

## 7. Complete List of Wrongly Marked Users

Result from live audit:

- none

## 8. Complete List of Early Discount Eligible Users

Current live result:

- none

Current count:

- early_discount_count: 0

## 9. Detailed Audit by Domain

### 9.1 User Flow Audit

Implemented:

- landing and marketing pages
- pricing page with Premium discount note
- legal onboarding and consent capture
- onboarding gating before normal product usage
- automatic 7-day trial activation path
- effective tier downgrade after trial expiry
- feature gates based on effective plan tier
- plans page and upgrade path
- GDPR delete with anonymized conversation retention

Gaps:

- no strong reactivation journey after cancellation or inactivity
- no dynamic pricing state for the early-access note

### 9.2 AI Flow Audit

Implemented:

- clear differentiation between Trial, Basic, Premium, and VIP in prompts
- tier-based context window and token limits
- intelligent upsell rules
- automatic medical-support disclaimer rules
- VIP-specific deeper analysis and typology guidance
- profile refresh from journal-derived AI analysis

Gaps:

- no dedicated reports persistence model
- no fully productized typology timeline or report history

### 9.3 Internal Automation Audit

Implemented:

- expire trials
- send trial warnings
- send journal reminders
- send daily plan reminders
- send wellbeing reminders
- send goal reminders
- send inactivity reminders
- send upgrade recommendations
- AI profile refresh
- weekly manual VIP audit

Gaps:

- no reactivation automation
- no explicit failed-job alerting channel

### 9.4 Manual VIP Audit

Implemented:

- manual VIP override is respected in effective tier logic
- skips discount applicability
- bypasses checkout/upgrade/cancel subscription flows
- bypasses trial notifications and trial expiry logic
- weekly audit validates consistency

Current live state:

- zero manual VIP users present

### 9.5 Early Discount Audit

Implemented:

- eligibility logic based on active user + ID threshold + no manual VIP
- checkout respects discount eligibility
- serializer returns derived eligibility correctly

Current live state:

- zero eligible users in current database snapshot

### 9.6 Support Automation Audit

Implemented:

- separate Support AI endpoint
- intent routing for account, billing, GDPR, technical, general topics
- technical or escalated requests can open/reuse tickets
- support tickets visible in admin

Gaps:

- no SLA tracking
- no queue ownership
- no internal note workflow
- no escalation dashboard for support operations

### 9.7 Backend / Infra Audit

Implemented:

- admin-managed scheduler for app jobs
- health endpoint for DB/cache readiness
- WAL-G backup daemon with backup schedule from platform config
- backup verification logs and backup config in admin

Gaps:

- no autoscaling
- no managed alerting
- restore workflow is still script-driven, not admin-driven

### 9.8 Dashboard Audit

Implemented:

- dashboards and observability logs exist for activity, support, analytics, quota, audit, backups
- admin sections for logs and operations are present

Gaps:

- low live data volume prevents business-quality interpretation
- missing richer cohort and funnel visualizations

### 9.9 Stripe Readiness Audit

Implemented:

- plan status handling
- upgrade and cancel flows
- internal fallback activation when Stripe is absent
- webhook processing and payment status reconciliation
- past-due and invalid-method notification logic

Gaps:

- environment still missing live Stripe credentials in this deployment snapshot
- readiness is architectural, not yet operationally live

## 10. Complete Scale Plan to 1,000 Subscribers

### Phase 1: 0 to 100 Subscribers

Objectives:

- validate onboarding completion
- validate trial-to-paid conversion
- ensure operational support responsiveness

Required actions:

- implement reactivation automation
- make early-access pricing state dynamic
- expand analytics funnel coverage
- strengthen support ticket handling workflow

KPIs:

- onboarding completion rate
- trial activation rate
- trial-to-paid conversion rate
- first-week retention

### Phase 2: 100 to 300 Subscribers

Objectives:

- stabilize retention motions
- improve monetization visibility

Required actions:

- cohort retention reporting
- cancellation reason capture
- win-back offers
- pricing and upsell experimentation

KPIs:

- churn rate
- reactivation rate
- premium upsell conversion
- support response time

### Phase 3: 300 to 600 Subscribers

Objectives:

- productize longitudinal value
- reduce operational fragility

Required actions:

- persistent AI reports
- explicit progress history
- queue or worker separation for heavier async tasks
- alerting for failed jobs and degraded health

KPIs:

- report engagement
- weekly active users
- failed scheduled job rate
- support ticket resolution time

### Phase 4: 600 to 1,000 Subscribers

Objectives:

- scale reliability, not just features
- prepare infra and operations for sustained paid volume

Required actions:

- worker separation for AI/profile updates/notification sends
- stronger database optimization and observability
- formal incident playbooks
- autoscaling strategy and capacity planning

KPIs:

- uptime
- p95 latency
- support backlog
- retention by tier
- net revenue retention

## 11. Product Growth Recommendations

1. Reduce onboarding friction while keeping legal clarity intact.
2. Make the first 72 hours of trial more outcome-oriented.
3. Expose visible continuity between journal, chat, plans, and progress.
4. Introduce milestone-based nudges instead of purely time-based nudges.
5. Create retention hooks around reports and typology for paid plans.
6. Use trust as a conversion lever: AI + GDPR + transparency is already a differentiator.
7. Add referral or invite loops after early positive outcomes.
8. Use support ticket closure feedback as a growth and quality signal.

## 12. Final Optimized Platform Vision

The optimized version of Doisense should look like this:

- all recurring operations are visible and controllable from admin
- trial, pricing, and billing states are aligned with live backend truth
- AI differentiation is evident in user outcomes, not just prompt logic
- reports and typology become persistent value surfaces for paid users
- support is AI-first but human-operable with full ticket lifecycle
- GDPR remains strict: personal data deleted, anonymized conversations retained
- growth loops exist for activation, retention, churn recovery, and monetization

## 13. Final Verdict

Doisense is ready for controlled growth.

What exists today is not a prototype. It is a coherent platform with:

- correct access logic
- strong tier-aware AI behavior
- working legal and GDPR foundations
- operational scheduler control in admin
- support escalation path
- backup automation and health visibility

What remains is not foundational rescue work. It is maturity work:

- retention systems
- growth instrumentation
- support operations depth
- reporting productization
- infrastructure hardening for scale

## 14. Recommended Next Build Order

1. Reactivation automation
2. Dynamic early-access pricing state
3. Persistent AI reports for Premium/VIP
4. Support SLA workflow and team operations
5. Backup restore operations surfaced in platform/admin
6. Funnel analytics and cohort dashboards
