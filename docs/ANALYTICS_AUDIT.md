# Step 5.3: Analytics & User Tracking Audit
**Status:** Completed  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Analytics and tracking implementation is **minimal and incomplete**:

- ✅ **GDPR consent framework** - Frontend tracks user consent preferences
- ✅ **Backend logging** - Conversations logged to AILog model
- ❌ **Zero external analytics** - No Google Analytics, Mixpanel, or similar
- ❌ **No product metrics** - Can't measure engagement, retention, feature usage
- ❌ **No funnel tracking** - Can't analyze registration → payment conversion
- ❌ **No A/B testing framework** - Can't test variations
- ❌ **No event tracking** - Missing feature usage events
- ❌ **No behavioral analytics** - Can't identify user cohorts or segments

**Impact:** Cannot make data-driven product decisions on engagement, retention, or monetization.

---

## 1. Current Implementation

### 1.1 GDPR Consent Framework

**Frontend:** `frontend/composables/useGdprConsent.ts`

Tracks three consent categories:
```typescript
{
  analytics: boolean     // Google Analytics, tracking pixels
  marketing: boolean     // Email marketing, ad platforms
  personalization: boolean // Non-essential personalization
}
```

**Storage:** Browser localStorage with key `gdpr_consent`  
**Persistence:** Survives page reload  
**Default:** All consent denied (`false`)

**User Actions:**
- `acceptAll()` → All consent granted
- `rejectAll()` → All consent rejected
- `saveCustom(custom)` → Custom selections

✅ **Status:** Properly implemented, GDPR compliant

### 1.2 Backend Logging

**Model:** `ai.models.AILog`
```python
class AILog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    module = models.CharField(max_length=50)
    prompt_tokens = models.IntegerField()
    response_tokens = models.IntegerField()
    cost = models.DecimalField(max_digits=8, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Used by:** Chat view to track AI API usage and cost  
✅ **Status:** Basic logging works

**Model:** `ai.models.Conversation`
```python
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    module = models.CharField(max_length=50)
    user_message = models.TextField()
    ai_response = models.TextField()
    plan_tier = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Used by:** Record every user → AI conversation  
✅ **Status:** Audit logging works (GDPR anonymization compatible)

---

### 1.3 What's NOT Tracked

| Metric | Status | Impact |
|--------|--------|--------|
| **User Engagement** | ❌ | Can't see daily/monthly active users |
| **Feature Usage** | ❌ | Don't know which features users prefer |
| **Retention Curves** | ❌ | Can't measure churn or retention rates |
| **Conversion Funnel** | ❌ | Don't know registration → payment conversion |
| **Onboarding Drop-off** | ❌ | Can't see where users abandon onboarding |
| **Journal Entry Frequency** | ❌ | Missing journaling behavior metrics |
| **Session Duration** | ❌ | Don't know how long users engage |
| **Geographic Data** | ❌ | No location-based insights |
| **Cohort Analysis** | ❌ | Can't compare user groups |
| **Error Tracking** | ❌ | No Sentry/Rollbar integration |

---

## 2. Required Analytics Infrastructure

To enable data-driven product decisions, Doisense needs:

### Phase 1: Basic Product Analytics (High Priority)
1. **Product Analytics Tool** (e.g., Mixpanel, Amplitude, PostHog)
   - Track key user actions: chat, journal, programs, payments
   - Measure engagement (MAU, DAU, feature adoption)
   - Analyze retention/churn cohorts
   
2. **Event Tracking System**
   - Frontend: React/Vue plugin to capture events
   - Backend: API methods to emit events
   - Server-side tracking with filtering

3. **Funnel Tracking**
   - Registration → Email verification → Onboarding → Chat
   - Chat → Payment initiation → Checkout → Payment confirmation
   - Identify drop-off points

### Phase 2: Advanced Analytics (Medium Priority)
4. **User Segmentation**
   - Behavioral: Chat users vs. Journal users vs. Both
   - Demographic: By language, country, plan tier
   - Engagement: Power users vs. Casual users

5. **Cohort Analysis**
   - Compare retention by signup date
   - Compare behavior by plan tier
   - Identify at-risk cohorts early

6. **A/B Testing Framework**
   - Experiment runner for onboarding variants
   - Feature flags for gradual rollouts
   - Statistical significance testing

### Phase 3: Monetization Analytics (Medium Priority)
7. **Revenue Metrics**
   - ARPU (Average Revenue Per User)
   - LTV (Lifetime Value)
   - CAC (Customer Acquisition Cost) - if ads exist
   - Churn rate and factors

8. **Pricing Analysis**
   - Plan tier distribution
   - Upsell conversion rates
   - Cancellation reasons (exit survey)

### Phase 4: Advanced Monitoring (Low Priority)
9. **Error Tracking** (Sentry/Rollbar)
   - Frontend JS errors
   - Backend exceptions
   - API failure rates

10. **Session Recording** (Hotjar/Logrocket - optional)
   - See how users interact
   - Playback problematic sessions

---

## 3. Recommended Analytics Stack

### Option 1: Open Source (PostHog)
**Pros:** Self-hosted, no vendor lock-in, GDPR friendly  
**Cons:** Requires DevOps overhead  
**Cost:** €0 (self-hosted) or €500+/month (managed)

```typescript
// Frontend setup
import posthog from 'posthog-js'
posthog.init('phc_...', { api_host: 'https://analytics.yourdomain.com' })
posthog.capturePageView()
posthog.capture('user_started_chat', { messageLength: 42 })
```

**Backend Integration:**
```python
from posthog import Posthog
posthog = Posthog('phc_...', host='https://analytics.yourdomain.com')
posthog.capture(user_id, 'ai_response_generated', {
    'tokens': 500,
    'plan_tier': 'premium'
})
```

### Option 2: Managed Service (Mixpanel)
**Pros:** Industry standard, great UX, no DevOps  
**Cons:** Third-party SaaS, vendor lock-in, privacy concerns  
**Cost:** $999+/month

**Privacy consideration:** Ensure GDPR compliance (data processing agreement)

### Option 3: Hybrid (Segment + Mixpanel)
**Pros:** Flexible, route to multiple destinations  
**Cons:** More complex setup  
**Cost:** $120-500/month (Segment) + analytics tools

---

## 4. Implementation Roadmap

### Week 1: Setup
- [ ] Choose analytics platform (PostHog recommended for GDPR)
- [ ] Deploy analytics infrastructure
- [ ] Create frontend event schema document
- [ ] Create backend event schema document

### Week 2: Frontend Tracking
- [ ] Install analytics SDK
- [ ] Wrap with GDPR consent check
- [ ] Track core events:
  - `page_view`
  - `user_signup` (after registration)
  - `user_login`
  - `onboarding_started`
  - `onboarding_completed` (with step count)
  - `chat_started`
  - `chat_message_sent`
  - `journal_entry_created`
  - `program_started`
  - `payment_initiated`
  - `payment_completed`
  - `payment_cancelled`

### Week 3: Backend Tracking
- [ ] Integrate analytics SDK
- [ ] Track server-side events (can't be bypassed)
- [ ] Events: AI response time, token usage, cost
- [ ] Events: Subscription state changes
- [ ] Events: Feature access attempts (including failures)

### Week 4: Dashboards & Reporting
- [ ] Create engagement dashboard (MAU, DAU, feature usage)
- [ ] Create funnel dashboard (registration → payment)
- [ ] Create cohort retention dashboard
- [ ] Create revenue dashboard

---

## 5. Key Events to Track

### User Events
```
user.signup
user.email_verified
user.trial_started
user.trial_expiring_soon (day 5, 6, 7)
user.trial_expired
user.payment.initiated
user.payment.completed
user.payment.failed
user.payment.cancelled
user.payment.refunded
user.subscription.upgraded
user.subscription.downgraded
user.subscription.cancelled
user.account.deleted
```

### Feature Events
```
onboarding.started
onboarding.step_completed (step: 1-6)
onboarding.completed
chat.started
chat.message_sent
chat.response_received
journal.entry_created
journal.question_viewed
program.started
program.day_completed
program.completed
profile.updated
report.generated
analytics.viewed
payment.plan_viewed
payment.pricing_viewed
```

### Error Events
```
error.api_failure
error.payment_failure
error.ai_error
error.validation_error
```

---

## 6. Dashboard Examples

### Engagement Dashboard
```
MAU: 245
DAU: 89 (36% engagement rate)
Avg. messages/user/day: 2.1
Chat users: 67%
Journal users: 45%
Both: 30%
```

### Funnel Dashboard
```
Registration:        1,000 (100%)
Email Verified:        850 (85%)
Onboarding Started:    800 (80%)
Onboarding Complete:   650 (65%)
First Chat:            580 (58%)
Payment Initiated:     120 (12%)
Payment Completed:      45 (4.5%)  ← Low conversion!
```

### Retention Dashboard
```
Cohort       | Week 1 | Week 2 | Week 4 | Week 8
Signup *     | 100%   | 42%    | 18%    | 8%
Jan Cohort   | 100%   | 45%    | 21%    | 10%
Feb Cohort   | 100%   | 38%    | 14%    | 6%
Trial Only   | 100%   | 35%    | 8%     | 2%
Paid Users   | 100%   | 68%    | 35%    | 18%
```

---

## 7. Privacy & GDPR Compliance

### Data Minimization
- Track only necessary events
- Anonymize user IDs (hash or pseudonym)
- Don't track PII (emails, etc.) in events
- Exclude content of messages/journal entries

### Consent Management
- Only track if `gdpr_consent.analytics = true`
- Disable all tracking if `gdpr_consent = false`
- Provide consent withdrawal mechanism

### Data Retention
- Delete analytics data after 12 months
- Purge on user account deletion (already implemented for ailog/conversations)

### Data Processing Agreement
- Sign DPA with analytics provider
- Ensure EU data residency if possible
- Regular security audits

---

## 8. Files to Modify/Create

**Frontend:**
- [ ] `frontend/plugins/analytics.client.ts` - Analytics SDK initialization with GDPR wrapper
- [ ] `frontend/composables/useAnalytics.ts` - Event tracking composable
- [ ] `frontend/pages/onboarding.vue` - Add onboarding events
- [ ] `frontend/pages/chat/index.vue` - Add chat events
- [ ] `frontend/pages/journal/index.vue` - Add journal events
- [ ] `frontend/pages/programs/index.vue` - Add program events

**Backend:**
- [ ] `backend/core/analytics.py` - Analytics SDK wrapper, event publishers
- [ ] `backend/ai/views_chat.py` - Emit AI events
- [ ] `backend/payments/views.py` - Emit payment events
- [ ] `backend/users/views.py` - Emit auth events

**Config:**
- [ ] `.env` - `ANALYTICS_API_KEY`, `ANALYTICS_HOST`
- [ ] `docker-compose.yml` - Analytics container (if self-hosted)

---

## 9. Success Metrics

After analytics implementation, measure:

### Engagement
- ✅ MAU should stabilize
- ✅ DAU/MAU ratio should be > 30%
- ✅ Chat users should be > 50% of active users

### Retention
- ✅ Week 2 retention should be > 40%
- ✅ Week 4 retention should be > 20%
- ✅ Paid users should have 2x retention vs. trial users

### Monetization
- ✅ Payment initiation rate > 10% of chat users
- ✅ Payment completion rate > 30% of initiated
- ✅ Trial → paid conversion > 5%

### Growth
- ✅ Cohort retention improves month-over-month
- ✅ Feature adoption increases quarter-over-quarter

---

## Next Steps

1. ✅ Audit completed
2. ❓ Choose analytics platform (recommend PostHog)
3. ❓ Set up infrastructure
4. ❓ Implement frontend tracking
5. ❓ Implement backend tracking
6. ❓ Create dashboards

---
