# Step 5: Feature Access Control Audit
**Status:** In Progress  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Feature access control in Doisense is **partially implemented but inconsistent**. The platform has 5 plan tiers (FREE, TRIAL, BASIC, PREMIUM, VIP) but:

- ✅ **Implemented:** Basic subscription gating (has_paid_access check)
- ✅ **Implemented:** AI capabilities differentiated by plan tier (response tokens, history window)
- ❌ **Missing:** Tier-specific feature feature access matrix
- ❌ **Missing:** Journal/Programs premium features enforcement
- ❌ **Missing:** Analytics/reporting access control
- ❌ **Missing:** Feature-level permission decorators
- ❌ **Missing:** Comprehensive documentation of what each tier can do

---

## 1. Current Implementation Status

### 1.1 User Model & Plan Tiers

**File:** `backend/users/models.py`

```
PLAN_CHOICES = [
    (PLAN_FREE, "Free"),
    (PLAN_TRIAL, "Trial"),
    (PLAN_BASIC, "Basic"),
    (PLAN_PREMIUM, "Premium"),
    (PLAN_VIP, "VIP"),
]
```

**Key Methods:**
- `is_in_trial()` - True if trial not expired
- `has_unlimited_platform_access()` - True if superuser/staff
- `effective_plan_tier()` - Returns tier considering trial expiry
- `has_paid_access()` - True if TRIAL|BASIC|PREMIUM|VIP (not FREE)
- `start_trial()` - Activates 7-day trial (idempotent)

✅ **Status:** Well implemented and tested

---

### 1.2 Chat Access Control

**File:** `backend/ai/views_chat.py`

**Current Controls:**
- Checks `has_paid_access()` - OK, blocks FREE users ✅
- **History window by tier:**
  - FREE: 0 (no context)
  - BASIC: 2 conversations
  - TRIAL: 4 conversations
  - PREMIUM: 6 conversations
  - VIP: 12 conversations
- **Response tokens by tier:**
  - FREE: 420
  - BASIC: 420
  - TRIAL: 640
  - PREMIUM: 800
  - VIP: 1200

✅ **Status:** Well differentiated by tier

---

### 1.3 Prompt Personalization by Tier

**File:** `backend/ai/prompt_builder.py`

**Current Controls:**
- `_get_chat_capability_instruction()` - Tier-specific system prompt
  - TRIAL: Guided preview, suggests paid plans
  - BASIC: Concise responses, limited reports
  - PREMIUM: Structured reflection, weekly summaries
  - VIP: Full longitudinal analysis, monthly reports, typology
- `_get_chat_guardrails()` - Upsell strategy varies by tier
  - VIP: No upsell (no need)
  - PREMIUM: Sparse upsell (VIP only if explicitly requested)
  - TRIAL: Intelligent upsell (frame as continuity)
  - BASIC: Standard upsell

✅ **Status:** Well differentiated and strategic

---

### 1.4 Journal Access Control

**File:** `backend/journal/views.py`

**Current Implementation:**
```python
def get(self, request):
    if not request.user.has_paid_access():
        return Response(
            {"detail": "Your trial or subscription has expired."},
            status=status.HTTP_403_FORBIDDEN,
        )
```

**Issues:**
- ❌ Only checks if user has paid access (no FREE tier)
- ❌ No differentiation between BASIC/PREMIUM/VIP
- ❌ No per-tier limits on entries
- ❌ No quota system documented

---

### 1.5 Programs (Guided Programs) Access Control

**File:** `backend/programs/views.py`

**Current Implementation:**
```python
def get(self, request, program_id, day_number):
    if not request.user.has_paid_access():
        return Response({"detail": "Your trial or subscription has expired."}, status=403)
    
    program = get_object_or_404(GuidedProgram, id=program_id, active=True)
    if program.is_premium and not request.user.has_paid_access():
        # This check is redundant!
        return Response({"detail": "This program requires a premium subscription."}, status=403)
```

**Issues:**
- ❌ `is_premium` check is redundant (already checked above)
- ❌ Doesn't differentiate between BASIC/PREMIUM/VIP
- ❌ Should check if user tier >= required tier
- ❌ No access to program progression tracking
- ❌ Model has `is_premium` but views don't properly use it

---

### 1.6 Wellbeing Checkin Access Control

**File:** `backend/core/views.py` - UserWellbeingCheckinCreateView

**Current Implementation:**
```python
permission_classes = [IsAuthenticated]
# Custom permission check needed but missing
```

**Issues:**
- ❌ No plan tier check at all
- ❌ Should require paid access
- ❌ Data likely accessible to all authenticated users

---

### 1.7 User Profile & Analytics Access Control

**File:** `backend/profiles/views.py` (needs to be checked)

**Issues (from architecture):**
- ❌ No mention of access control by tier
- ❌ Profile read/write permissions unclear
- ❌ Analytics data (if any) not protected by tier

---

### 1.8 Payment Views

**File:** `backend/payments/views.py`

**Status:** Payment integration uses Stripe, basic plan activation implemented.
- ✅ Plan tier validation: `VALID_PLAN_TIERS = {"basic", "premium", "vip"}`
- ✅ Price ID mapping to tiers
- ✅ Plan activation logic

---

## 2. Feature Access Matrix

### 2.1 Proposed Feature Matrix (TODO)

| Feature | FREE | TRIAL | BASIC | PREMIUM | VIP |
|---------|------|-------|-------|---------|-----|
| **AI Chat** | ❌ | ✅ Limited | ✅ Limited | ✅ Better | ✅ Full |
| Chat history | ❌ | 4 msgs | 2 msgs | 6 msgs | 12 msgs |
| Response tokens | N/A | 640 | 420 | 800 | 1200 |
| **Journal** | ❌ | ✅ | ✅ | ✅ | ✅ |
| Entries/month | N/A | Unlimited | Unlimited | Unlimited | Unlimited |
| Reports/month | N/A | 0 | 1 | 4 | Unlimited |
| **Programs** | ❌ | ✅ Basic only | ✅ All | ✅ All | ✅ All |
| Basic programs | N/A | ✅ | ✅ | ✅ | ✅ |
| Premium programs | N/A | ❌ | ❌ | ✅ | ✅ |
| **Analytics** | ❌ | ❌ | ❌ | ✅ | ✅ |
| Weekly reports | N/A | N/A | N/A | ✅ | ✅ |
| Monthly reports | N/A | N/A | N/A | ❌ | ✅ |
| Typology insights | N/A | N/A | N/A | ❌ | ✅ |

---

## 3. Issues Found

### Critical
1. **❌ Journal has no tier differentiation** - All paid users get same access
2. **❌ Programs access control is broken** - `is_premium` check is redundant
3. **❌ Wellbeing checkins lack access control** - Not checking for paid access
4. **❌ No quota system** - Journal entries, reports, etc. have no limits

### High Priority
5. **❌ No analytics/reporting module** - Not mentioned in views/models
6. **❌ Profile update rules unclear** - No access control documented
7. **❌ No feature permission decorators** - Manual checks scattered throughout

### Medium Priority
8. **❌ Frontend doesn't know tier capabilities** - Should expose feature matrix
9. **❌ No audit logging** - Can't track feature access by tier
10. **❌ Upsell CTAs missing** - Should trigger when user hits quotas

---

## 4. Implementation Plan

### Phase 1: Fix Critical Issues (Priority)
1. Fix programs access control (proper tier checking)
2. Add wellbeing checkin access control
3. Implement journal quota system (track entries/month)
4. Create permission decorator for feature access

### Phase 2: Implement Missing Features (Features)
5. Create analytics/reporting module with tier access
6. Add feature matrix API endpoint
7. Implement audit logging for feature access
8. Add quota tracking models

### Phase 3: Frontend Integration (Polish)
9. Expose feature matrix to frontend
10. Show quota status (e.g., "1/4 reports remaining")
11. Trigger paywall CTAs when quotas reached
12. Add feature cards showing what's included in each tier

---

## 5. Files Involved

**Current implementation:**
- ✅ `backend/users/models.py` - Plan tier definitions
- ✅ `backend/ai/views_chat.py` - Chat access control
- ✅ `backend/ai/prompt_builder.py` - Tier-specific prompts
- ❌ `backend/journal/views.py` - Journal access (needs tier differentiation)
- ❌ `backend/programs/views.py` - Programs access (needs fixing)
- ❌ `backend/core/views.py` - Wellbeing checkin access (needs adding)
- ❌ `backend/profiles/views.py` - Profile access (needs checking)

**To be created:**
- `backend/core/permissions.py` - Feature permission decorators
- `backend/core/quotas.py` - Quota tracking logic
- `backend/core/models.py` - Update with quota models (if needed)
- `backend/core/migrations/` - Migration for quota tracking
- Tests for all access control logic

---

## Next Steps

1. ✅ Audit completed - Issues identified
2. ❓ Create feature permission decorators
3. ❓ Fix journal access control
4. ❓ Fix programs access control
5. ❓ Add wellbeing access control
6. ❓ Implement quota system
7. ❓ Create analytics module
8. ❓ Add frontend feature matrix API
9. ❓ Test all access control paths

---
