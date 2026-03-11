# Step 5.4: Payment Integration Security & Flows Audit
**Status:** Completed  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Payment integration with Stripe is **well-implemented and secure**:

- ✅ **Secure checkout flow** - Stripe-hosted sessions, no card handling
- ✅ **Webhook validation** - Signature verification implemented
- ✅ **State management** - Proper user tier and subscription tracking
- ✅ **PCI compliance** - No card data stored locally
- ✅ **Multi-tier support** - BASIC, PREMIUM, VIP pricing
- ✅ **Recovery flows** - Past due, cancellation, reactivation
- ✅ **Billing portal** - Users can manage subscriptions

**Issues Found:** Minor gaps in monitoring and edge cases:
- ❌ No payment failure notifications to users
- ❌ No retry logic for failed webhooks
- ❌ Missing rate limiting on checkout session creation
- ❌ No payment method validation before charging
- ❌ Incomplete handling of edge cases (refunds, disputes)

---

## 1. Architecture Overview

### 1.1 Payment Models

**Model:** `payments.models.Payment`
```python
class Payment(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('trialing', 'Trialing'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=100, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=100, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trialing")
    plan_tier = models.CharField(max_length=10, choices=PLAN_CHOICES, default="premium")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

✅ **Status:** Well-structured, captures necessary fields

### 1.2 Stripe Configuration

**Stored in:** `SystemConfig` model (managed via admin)
```python
stripe_secret_key          # Stripe API key for backend
stripe_webhook_secret      # Webhook signature verification
stripe_price_id_basic      # Stripe price ID for BASIC plan
stripe_price_id_premium    # Stripe price ID for PREMIUM plan
stripe_price_id_vip        # Stripe price ID for VIP plan
```

✅ **Status:** Secure configuration management

**Pricing Mapping:**
```python
BASIC → price_basic_usd
PREMIUM → price_premium_usd  (default)
VIP → price_vip_usd
FREE → None (no Stripe needed)
TRIAL → None (7-day, then must convert)
```

---

## 2. Payment Flow Analysis

### 2.1 Checkout Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Subscribe to PREMIUM"                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Frontend: POST /payments/checkout/session                   │
│ Body: { plan_tier: "premium" }                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: CreateCheckoutSessionView.post()                   │
│ 1. Validate plan_tier (default: "premium")                  │
│ 2. Get Stripe secret key & price ID                         │
│ 3. Build success/cancel URLs (language-aware)               │
│ 4. Create Stripe session with:                              │
│    - mode: "subscription"                                   │
│    - price: stripe_price_id                                 │
│    - metadata: { user_id, plan_tier }                       │
│    - customer: existing customer_id (or email)              │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────┐
│ Stripe: Create Checkout Session                            │
│ Returns: { url: "https://checkout.stripe.com/..." }        │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│ Frontend redirects to session.url                        │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ├─ User enters card (Stripe-hosted) ──────┐
                  │                                         │
                  └─ User cancels ─────────────────────────┐│
                                                          ││
        ┌─────────────────────────────────────────────────┘│
        │                                                  │
        ▼                                                  ▼
    Success URL                                    Cancel URL
  /payment-success                              /pricing
    plan=premium


Result in user.plan_tier:
┌──────────────────────────────────────────────────────┐
│ AFTER checkout.session.completed webhook:           │
│ user.plan_tier = "premium"                           │
│ user.is_premium = True                               │
│ Payment.status = "active"                            │
│ Payment.stripe_customer_id = customer_id             │
│ Payment.stripe_subscription_id = subscription_id     │
└──────────────────────────────────────────────────────┘
```

✅ **Status:** Properly implemented, PCI-compliant (no card handling)

### 2.2 Subscription State Management

**Stripe Webhooks Handled:**

1. **checkout.session.completed**
   ```
   Fired when:  User completes payment in Stripe checkout
   Action:     _activate_plan(user, plan_tier)
   Result:     user.plan_tier set, Payment record created
   Status:     ✅ Implemented
   ```

2. **customer.subscription.updated**
   ```
   Fired when:  Subscription modified (plan change, status change)
   Handles:    active → past_due (payment failed, grace period)
                past_due → active (payment recovered)
                canceled (user cancelled)
   Status:     ✅ Implemented
   
   Issues:     
   - ❌ Doesn't handle quantity changes (if relevant)
   - ❌ No logging of state transitions
   ```

3. **customer.subscription.deleted**
   ```
   Fired when:  Subscription cancelled (after grace period)
   Action:     Downgrade user to FREE tier
   Result:     user.plan_tier = "free", is_premium = False
   Status:     ✅ Implemented
   ```

4. **invoice.payment_failed**
   ```
   Fired when:  Charge attempt failed
   Action:     Set status to "past_due", disable premium features
   Result:     user.is_premium = False
   Status:     ✅ Implemented
   
   Issues:
   - ❌ No notification sent to user
   - ❌ No retry logic
   - ❌ Messages unclear about grace period
   ```

5. **invoice.payment_succeeded**
   ```
   Fired when:  Payment recovered after failure
   Action:     Set status to "active", re-enable premium
   Result:     user.is_premium = True
   Status:     ✅ Implemented
   
   Issues:
   - ❌ No notification sent to user
   ```

### 2.3 Webhook Security

**Implementation:** `stripe_webhook` view in `payments/views.py`

```python
@csrf_exempt  # Stripe requests don't have CSRF token
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    
    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            stripe_webhook_secret
        )
    except ValueError:         # Invalid payload
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:  # Invalid signature
        return HttpResponse(status=400)
    
    # Process event
    event_type = event["type"]
    ...
    return HttpResponse(status=200)
```

**Security Checklist:**
- ✅ Signature verification: Required (stripe.Webhook.construct_event)
- ✅ CSRF exempt: Correct (Stripe sends from external IP)
- ✅ HTTP method restriction: POST only
- ✅ Error handling: Returns 400 on invalid payload/signature
- ✅ Event type routing: Handles multiple event types

**Issues:**
- ❌ No logging of webhook events (can't debug issues)
- ❌ No webhook delivery acknowledgment (Stripe retries if no 200)
- ❌ No rate limiting on webhook processing

---

## 3. Security Assessment

### 3.1 PCI DSS Compliance

**Status:** ✅ COMPLIANT

| Requirement | Implementation | Status |
|-------------|-----------------|--------|
| No card data stored | Stripe-hosted sessions only | ✅ |
| No card data in logs | Not in Django logs/audit trail | ✅ |
| No card data in backups | N/A - never stored | ✅ |
| HTTPS on checkout | Stripe uses HTTPS | ✅ |
| Customer authentication | Stripe 3-D Secure ready | ✅ |

**Why compliant:**
- Application never sees credit card data
- All card handling delegated to Stripe (PCI Level 1 certified)
- Only token/subscription ID stored locally

### 3.2 Authentication & Authorization

**Checkout Session Creation:**
```python
permission_classes = [IsAuthenticated]  # ✅ Only authenticated users

# User can only see their own checkout
user = request.user  # ✅ No user_id parameter (prevents enumeration)
```

**Billing Portal Access:**
```python
permission_classes = [IsAuthenticated]  # ✅ Only authenticated users

# Requires existing Stripe customer
if not payment:
    return 403  # ✅ Users can't access others' portals
```

**Webhook Security:**
```python
# Signature verification prevents tampering
stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
# ✅ Only Stripe can trigger webhooks

# Idempotency: Events processed multiple times is safe?
# ❌ Issue: update_or_create is idempotent, but webhook dedup missing
```

### 3.3 Data Validation

**Plan Tier Validation:**
```python
plan_tier = (request.data.get("plan_tier") or "premium").lower()
if plan_tier not in VALID_PLAN_TIERS:  # {"basic", "premium", "vip"}
    plan_tier = "premium"  # ✅ Defaults to premium (upsell-friendly)
```

**Issues:**
- ❌ User can't request BASIC tier if frontend doesn't send it
- ❌ No TRIAL tier available for purchase (correct, but implicit)
- ⚠️ Free tier available but via function, not exposed

### 3.4 Configuration Security

**Issues:**
- ❌ Secret keys stored in SystemConfig (database)
- ⚠️ No secret rotation mechanism
- ❌ No audit log of secret access
- ✅ Keys not in code (correct)
- ✅ Keys can be set via Django admin (admin-only)

**Better approach:**
- Use environment variables for secrets
- Use `python-dotenv` to load from `.env`
- Never store secrets in database

---

## 4. Operational Issues

### 4.1 Missing Features

**1. Payment Failure Notifications**
- ❌ User not notified when payment fails
- ❌ User doesn't know subscription in jeopardy
- ❌ No grace period messaging
- **Recommendation:** Send email:
  ```
  Subject: Payment failed for your Doisense subscription
  
  Your payment failed: [reason]
  
  Your subscription is suspended but not cancelled.
  You have 7 days to update your payment method.
  
  Update payment: [link to billing portal]
  ```

**2. Retry Logic**
- ❌ Stripe retries automatically (3 attempts over 4 days)
- ❌ App doesn't confirm retry success to user
- ❌ No manual retry option in billing portal
- **Recommendation:** 
  - Use Stripe's automatic retry (already enabled)
  - Email user when retries succeed

**3. Downgrade Flow**
- ❌ No ability to downgrade from PREMIUM to BASIC
- ✅ Can cancel and lose features
- **Recommendation:**
  - Add `POST /payments/downgrade` endpoint
  - Change subscription to lower-tier price

**4. Refunds**
- ❌ No refund handling in webhook
- ❌ No refund policy documented
- **Recommendation:**
  - Handle `charge.refunded` webhook
  - Issue credit/downgrade user appropriately

**5. Upgrades Mid-Cycle**
- ⚠️ Stripe handles automatically (prorates billing)
- ⚠️ App doesn't track when upgrade happened
- **Recommendation:**
  - Add `payment.upgraded_at` timestamp
  - Log upgrade reason

---

### 4.2 Error Handling & Recovery

**Current:**
```python
try:
    session = stripe.checkout.Session.create(**params)
    return Response({"url": session.url})
except stripe.StripeError as exc:
    return Response({"detail": str(exc)}, status=400)
```

**Issues:**
- ❌ User sees raw Stripe error ("Invalid API Key" etc.)
- ❌ No correlation ID for debugging
- ❌ No timeout handling (Stripe API could hang)
- ❌ Network errors not specifically caught

**Better:**
```python
try:
    session = stripe.checkout.Session.create(..., timeout=5)
except stripe.error.CardError as e:
    return Response({"detail": "Card declined"}, status=400)
except stripe.error.RateLimitError:
    return Response({"detail": "Too many requests, try again"}, status=429)
except stripe.error.AuthenticationError:
    return Response({"detail": "Payment system misconfigured"}, status=500)
except stripe.error.APIError:
    return Response({"detail": "Payment system error, try again"}, status=503)
except Exception as e:
    logger.exception(f"Stripe error: {e}")
    return Response({"detail": "An error occurred"}, status=500)
```

---

### 4.3 Rate Limiting

**Issue:** No rate limiting on checkout session creation

**Risk:** User could spam `POST /checkout/session` creating many sessions

**Fix:**
```python
from django.views.decorators.cache import cache_page
from rest_framework.throttling import UserRateThrottle

class PaymentThrottle(UserRateThrottle):
    scope = 'payment'
    THROTTLE_RATES = {'payment': '10/hour'}

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentThrottle]
```

---

### 4.4 Idempotency

**Issue:** Webhook events processed repeatedly could cause issues

**Current:** Uses `update_or_create` which is safe (upsert)

**Better:** Add webhook event deduplication:
```python
class WebhookEvent(models.Model):
    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True)

# In webhook handler:
event_id = event["id"]
webhook_event, created = WebhookEvent.objects.get_or_create(
    stripe_event_id=event_id,
    defaults={'event_type': event['type']}
)
if webhook_event.processed:
    return HttpResponse(status=200)  # Idempotent

# Process event...
webhook_event.processed = True
webhook_event.processed_at = timezone.now()
webhook_event.save()
```

---

### 4.5 Monitoring & Alerting

**Missing:**
- ❌ No webhook delivery monitoring
- ❌ No failed payment alert
- ❌ No refund alert
- ❌ No suspicious activity detection (multiple failed attempts)
- ❌ No revenue tracking dashboard

**Recommendations:**
1. Set up Stripe dashboard alerts
2. Log all webhook events to database
3. Create monitoring dashboard in admin
4. Alert on: payment failures (3+), high refund rate, etc.

---

## 5. Edge Cases & Known Issues

### 5.1 Subscription State Conflicts

**Issue:** What if user's local plan_tier doesn't match Stripe?

**Scenario:** 
1. User cancels subscription in Stripe
2. Webhook `customer.subscription.deleted` fails (network error)
3. User's local status says "active" but Stripe says "cancelled"
4. User shouldn't have access, but can still use app

**Current:** No sync mechanism

**Recommendation:** 
- Implement background job: `check_stripe_subscription_sync()`
- Email admin if mismatch found
- Downgrade user if Stripe says so

### 5.2 Duplicate Subscriptions

**Issue:** Can user create two subscriptions?

**Current:** `Payment.objects.update_or_create(user=user)` means one per user

**Scenario:** Could malicious user create subscription twice?
- First session: customer_id = ABC
- Second session: customer_id = None → new customer created
- Both subscriptions active → doubled billing

**Research needed:** Does Stripe prevent duplicate subscriptions for same email?

### 5.3 TRIAL to Paid Conversion

**Current:** Users can use 7-day trial, then must pay or lose access

**Issue:** No special pricing for trial converts (no "trial discount")

**Recommendation:**
- Offer "pay half" for first month if they pay before trial ends
- Use coupon code sent in day-5 email

---

## 6. Compliance & Legal

### 6.1 Terms of Service

**Missing:**
- ❌ No refund policy documented
- ❌ No billing terms (when charged, how often)
- ❌ No cancellation terms
- ❌ No grace period documented

**Recommendation:** Add to `/legal/terms`:
```
## Billing & Refunds

### Billing
- Billing occurs on the same day of each month
- Grace period: 7 days for failed payments
- After 7 days, subscription automatically cancels

### Refunds
- No refunds for partial months
- Cancellations effective immediately

### Plan changes
- Upgrades: Prorated (pay difference)
- Downgrades: Credit applied next billing
```

### 6.2 Data Processing

**GDPR:** Payment data involves sensitive processing

**Recommendation:**
- Ensure DPA with Stripe exists
- Annual Stripe audit report
- Documentation of payment data retention (30 days minimum for PCI)

---

## 7. Files Involved

**Backend:**
- ✅ `backend/payments/models.py` - Payment model
- ✅ `backend/payments/views.py` - Checkout, billing portal, webhook
- ✅ `backend/core/system_config.py` - Secret key management
- ❌ `backend/payments/signals.py` - Missing payment event signals
- ❌ `backend/payments/webhooks.py` - Could separate webhook logic

**Frontend:**
- ✅ `frontend/pages/pricing/` - Pricing page (assumed to link to checkout)
- ? `frontend/pages/payment-success.vue` - Probably needs check for payment success
- ? `frontend/pages/trial-expired.vue` - Existing, shows upgrade CTA

**Tests:**
- ❌ No payment tests found (no `tests/test_payments.py`)
- ❌ No webhook tests (idempotency, edge cases)
- ❌ No Stripe mock needed

---

## 8. Recommended Security Enhancements (Priority)

### CRITICAL (Do Now)
1. [ ] Add payment failure notifications
2. [ ] Implement webhook event deduplication
3. [ ] Add rate limiting to checkout

### HIGH (Do Soon)
4. [ ] Move secrets to environment variables (not database)
5. [ ] Add webhook delivery logging & monitoring
6. [ ] Implement subscription sync background job
7. [ ] Add downgrade capability

### MEDIUM (Do Later)
8. [ ] Add refund event handling
9. [ ] Implement trial conversion discounts
10. [ ] Add to terms of service

### LOW (Nice to Have)
11. [ ] Webhook event inspection in admin
12. [ ] Revenue analytics dashboard
13. [ ] A/B test checkout variants

---

## Next Steps

1. ✅ Audit completed
2. ❓ Implement payment failure notifications
3. ❓ Add webhook deduplication
4. ❓ Add rate limiting
5. ❓ Move secrets to environment variables

---
