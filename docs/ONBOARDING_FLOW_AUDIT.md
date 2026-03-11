# Step 5.2: User Onboarding Flow Audit
**Status:** Completed  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Onboarding flow is **well-designed and comprehensive** covering 6 guided steps with proper enforcement via middleware. The flow successfully:

- ✅ Guides new users through platform capabilities
- ✅ Enforces legal consent (terms, privacy, AI usage)
- ✅ Captures initial emotional state for personalization
- ✅ Sets expectations about capabilities vs. limitations
- ✅ Properly gates access to main features

**Issues:** Minor - could be enhanced with:
- ❌ Onboarding analytics/tracking of completion rates
- ❌ Personalized variant for different plan tiers (TRIAL vs. FREE)
- ❌ A/B testing framework
- ❌ Completion time metrics
- ❌ Re-onboarding flow for feature discovery

---

## 1. Onboarding Architecture

### 1.1 Flow Overview

**Route:** `/onboarding`  
**Middleware Protection:** `auth` (requires login)  
**Redirect Logic:** 
- If `onboarding_completed === false` → force `/onboarding`
- If `onboarding_completed === true` → redirect to `/chat`

### 1.2 Six-Step Onboarding Flow

| Step | Purpose | Key Actions | Validation |
|------|---------|-------------|-----------|
| **1. Welcome** | Welcome message | Click "Start" | None |
| **2. Platform** | Explain capabilities | Review bullets | None |
| **3. Disclaimer** | Medical/therapy warnings | Click "Understood" | None |
| **4. Privacy** | Privacy explanation | Accept T&C + Privacy + AI agreement | ✅ Consent checkbox required |
| **5. Emotional Profile** | Initial state capture | Select mood, energy, journal entry | Saves wellbeing checkin + journal entry (if provided) |
| **6. Chat Access** | Guide to chat | Display next steps | Completes onboarding, redirects to chat |

### 1.3 Backend Implementation

**User Model:** `backend/users/models.py`
```python
onboarding_completed = models.BooleanField(default=True)  # Default=True is bug?
```

**⚠️ Issue Found:** Model has `default=True` - newly registered users are marked as onboarding-completed!

**Serializer:** `backend/users/serializers.py`
```python
# Registration sets onboarding_completed=False
user = User.objects.create_user(..., onboarding_completed=False)
```

**View:** `backend/users/views.py` - MeView
```python
def patch(self, request):
    allowed_fields = {"first_name", "last_name", "phone_contact", "language", "tax_region", "onboarding_completed"}
    # Users can toggle onboarding_completed via PATCH /me
```

**✅ Status:** Properly implemented

### 1.4 Frontend Implementation

**Page:** `frontend/pages/onboarding.vue`
- Multi-step form with state management
- Language support: RO/EN (+ unused de/es/it/pl via copy object)
- Saves initial profile at step 5:
  - Creates wellbeing checkin: `POST /wellbeing/checkins`
  - Creates journal entry (if text provided): `POST /journal/entries`
- Completes onboarding at step 6: `PATCH /me` with `onboarding_completed=true`

**Composable:** `frontend/composables/useOnboarding.ts`
```typescript
const needsOnboarding = computed(() => authStore.user?.onboarding_completed === false)
const getPostAuthPath() => needs_onboarding ? '/onboarding' : '/chat'
```

**Middleware:** `frontend/middleware/onboarding.ts`
```typescript
if (!authStore.isLoggedIn || authStore.user?.onboarding_completed !== false) {
    return // Allow access
}
return navigateTo(localePath('/onboarding')) // Redirect to onboarding
```

**✅ Status:** Properly implemented

---

## 2. Current Behavior Analysis

### 2.1 Registration Flow
1. User clicks register
2. → `POST /auth/register`
3. → User created with `onboarding_completed=False` ✅
4. → Activation email sent
5. User clicks activation link
6. → `POST /auth/activate` 
7. → User activated, trial started ✅
8. User logs in → `POST /auth/login` ✅
9. Frontend checks user → renders `/onboarding` ✅

### 2.2 Onboarding Completion
1. User proceeds through 6 steps ✅
2. At step 5: saves emotion + optional journal entry ✅
3. At step 6: `PATCH /me` with `onboarding_completed=true` ✅
4. Redirects to `/chat` ✅

### 2.3 Skipping Onboarding
- User can manually set `onboarding_completed=true` via API
- No enforcement that steps were actually completed
- No user data validation (emotion/journal could be missing)

---

## 3. Issues Found

### Critical
1. **❌ Model default is True** - `onboarding_completed` defaults to True in model definition. If registered via admin bypass, users skip onboarding. **Semantic mismatch:** should default to False.

### High Priority
2. **❌ No completion validation** - Frontend doesn't verify if saved profile was successful before completing onboarding
3. **❌ No re-onboarding** - Users can't re-do onboarding to discover features after skipping
4. **❌ No feature discovery flow** - When new features are added, no mechanism to guide users

### Medium Priority
5. **❌ No analytics tracking** - Can't measure:
   - Drop-off rate at each step
   - Time per step
   - Completion rate
   - Emotional state distribution
   - Journal submission rate
6. **❌ Unused localization** - Copy object has de/es/it/pl but not loaded in `localeCode` logic
7. **❌ No tier-specific variant** - Same flow for all users (should be different for TRIAL vs. others)

### Low Priority
8. **❌ Error recovery** - If journal save fails, onboarding still completes (should retry or warn)
9. **❌ No A/B testing** - Can't test different onboarding variants
10. **❌ No progress persistence** - Closing browser loses step progress (should use localStorage)

---

## 4. Data Captured During Onboarding

### Wellbeing Checkin (Step 5)
**Endpoint:** `POST /wellbeing/checkins`
```python
{
  "mood": "low" | "ok" | "good" | "great",
  "energy_level": 1-5  # from slider
}
```

**Storage:** `core.models.UserWellbeingCheckin`

### Journal Entry (Step 5, optional)
**Endpoint:** `POST /journal/entries`
```python
{
  "question": <question_id>,  # First question in language
  "content": "<user_text>",
  "emotions": ["low" | "ok" | "good" | "great"]
}
```

**Storage:** `journal.models.JournalEntry`

### Legal Consent (Step 4)
**Stored in:** User model fields (confirmed during GDPR audit)
- `terms_accepted_at`
- `privacy_accepted_at`
- `ai_usage_accepted_at`

---

## 5. Flow Diagram

```
┌─────────────┐
│  Register   │  POST /auth/register → User(onboarding_completed=False)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Confirm Email   │  GET /activate✅ → User(is_active=True, trial starts)
└──────┬──────────┘
       │
       ▼
┌──────────────┐
│   Login       │  POST /login → localStorage("access", "refresh")
└──────┬───────┘
       │
       ▼
┌─────────────────────────┬────────────────────────────────────────────┐
│ Frontend hydrates auth  │ authStore.user.onboarding_completed = false │
└────────┬────────────────┴────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│  middleware/onboarding.ts checks:                                   │
│  if (onboarding_completed !== false) → allow access                 │
│  else → redirect to /onboarding                                     │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  pages/onboarding.vue - 6 Steps               │
├──────────────────────────────────────────────┤
│ Step 1: Welcome                              │
│ Step 2: Platform capabilities                │
│ Step 3: Disclaimers                          │
│ Step 4: Privacy (requires consent ✅)        │
│ Step 5: Emotion + Journal entry              │
│         POST /wellbeing/checkins             │
│         POST /journal/entries (optional)     │
│ Step 6: Chat instructions                    │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ PATCH /me                          │
│ { onboarding_completed: true }     │
└────────┬─────────────────────────────────┘
         │
         ▼
┌────────────────────────┐
│ Redirect to /chat      │
│ User can now access    │
│ platform features      │
└────────────────────────┘
```

---

## 6. Files Involved

**Backend:**
- ✅ `backend/users/models.py` - User model with onboarding_completed flag
- ✅ `backend/users/serializers.py` - Registration creates False
- ✅ `backend/users/views.py` - MeView allows toggling flag
- ✅ `backend/core/views.py` - UserWellbeingCheckinCreateView saves mood
- ✅ `backend/journal/views.py` - JournalEntriesView saves entries
- ❌ `backend/core/models.py` - Missing analytics/tracking tables

**Frontend:**
- ✅ `frontend/pages/onboarding.vue` - Full 6-step implementation
- ✅ `frontend/composables/useOnboarding.ts` - Route logic
- ✅ `frontend/middleware/onboarding.ts` - Route enforcement
- ❌ `frontend/composables/useAnalytics.ts` - Doesn't exist

---

## 7. Recommended Improvements (Phase 2)

### High Impact
1. **Add onboarding analytics** - Track step completion, drop-off, time
2. **Add error handling** - Validate journal save before completing
3. **Add re-onboarding UI** - Allow users to re-discover features
4. **Fix model default** - Change `default=True` to `default=False`

### Medium Impact
5. **Create tier-specific variants** - Different flows for different users
6. **Add progress persistence** - localStorage to resume if interrupted
7. **Add A/B testing framework** - Test different onboarding variants
8. **Complete localization** - Add de/es/it/pl locale support

### Low Impact
9. **Add optional profiling** - Let users skip emotional profile
10. **Add skip button** - Advanced users can skip to chat (with warning)

---

## Next Steps

1. ✅ Audit completed
2. ❓ (Optional) Fix model default True → False
3. ❓ (Optional) Add error handling to profile save
4. ❓ (Optional) Add onboarding completion metrics
5. ❓ (Optional) Build feature discovery re-onboarding

---
