# Stripe Payments System Audit
**Data auditului**: 13 martie 2026  
**Status**: ⚠️ Cu probleme care necesită reparații

---

## 1. Configurație Stripe

### ✅ Aspect bun
- **Environment variables** corecte în `.env.example` și `docker-compose.yml`
- **Variabile noi pentru Product IDs**: `STRIPE_PRODUCT_ID_BASIC`, `STRIPE_PRODUCT_ID_PREMIUM`, `STRIPE_PRODUCT_ID_VIP` sunt definite
- **Django settings** au getters pentru secret keys și webhook secrets
- **System Config model** are câmpuri pentru `stripe_product_id_*` și `stripe_price_id_*`

### ❌ Probleme identificate

#### Problem 1: Neconzistență între Price IDs vs Product IDs
**Severitate**: MEDIE  
**Descriere**: Sistemul folosește Price IDs în checkout (`get_stripe_price_id_for_tier()`), dar Product IDs nu sunt utilizate nicăieri.  
**Impactul**: Dacă Stripe schimbă pricing modelul, sistemul se va rupe.  
**Recomandare**: 
- Decide între folosirea Product IDs (mai corect) sau Price IDs
- Documentează mapping-ul

#### Problem 2: Duplicare `_price_id_to_tier` mapping
**Severitate**: MEDIE  
**Descriere**: Funcția `_price_id_to_tier()` este definită în 3 locuri:
- `backend/payments/views.py` (linia ~168)
- `backend/payments/management/commands/sync_subscriptions.py` (linia ~15)
- Ar trebui centralizată în `core/system_config.py`

**Impactul**: Dacă Price IDs se schimbă, trebuie update în 3 locuri.  
**Recomandare**: Refactorizati în `core/system_config.py` și exportati din `system_config` în toate locurile.

#### Problem 3: Lipsă getters pentru Product ID reverse-mapping
**Severitate**: JOASĂ  
**Descriere**: Funcția `get_stripe_product_id_for_tier()` există dar nu avem o funcție inversă.  
**Recomandare**: Adaugati `_product_id_to_tier()` în system_config dacă se decide să se folosească Product IDs.

---

## 2. Model de date și baza de date

### ✅ Aspect bun
- **Payment model** are:
  - Status tracking (active, cancelled, past_due, trialing)
  - Plan tier tracking (basic, premium, premium_discounted, vip)
  - Billing cycle dates (current_period_end, cancel_at_period_end)
  - Stripe identifiers (customer_id, subscription_id)
  - Timestamps pentru audit trail

- **StripeWebhookEvent model** are:
  - Event ID unic (prevent duplicates)
  - Status tracking (received, processed, ignored, failed)
  - Delivery attempt counting
  - Payload storage pentru debugging
  - Error messages
  - Database indexes pentru query performance

### ❌ Probleme identificate

#### Problem 4: Lipsă Product ID tracking în Payment
**Severitate**: JOASĂ  
**Descriere**: Payment model nu stochează `stripe_product_id` - doar `stripe_subscription_id`.  
**Impactul**: Dacă schimbam de la Price IDs la Product IDs, nu putem reconstitui subscription history.  
**Recomandare**: Adaugati câmp optional `stripe_product_id` în Payment model.

#### Problem 5: Lipsă migration pentru product_id fields
**Severitate**: MEDIE  
**Descriere**: Migration `0023_add_stripe_product_ids.py` a fost creată dar nu testată.  
**Recomandare**: Rulati migration și testati pe staging.

---

## 3. API Endpoints și Views

### ✅ Aspect bun

- **CreateCheckoutSessionView**:
  - Throttling (6 per hour)
  - Feature gating (`@require_feature("payment_checkout")`)
  - Fallback la internal activation dacă Stripe nu e configurat
  - Suportă early discount promos
  - Metadata tracking pentru audit

- **UpgradeSubscriptionView**:
  - Throttling (12 per hour)
  - In-place subscription modification
  - Proration handling (`proration_behavior="always_invoice"`)
  - Feature gating

- **CancelSubscriptionView**:
  - Soft cancellation la period end
  - Fallback dacă Stripe nu e configurat
  - Billing cycle tracking

- **SubscriptionStatusView**:
  - Informații cuprinzătoare despre subscription status
  - Manual VIP override handling
  - User-friendly response format

- **SavedCardView**:
  - Securizat (payment methods în Stripe, nu local)
  - Extrage din Stripe doar branded info (brand, last4, exp dates)

- **PromoStateView**:
  - Calculează dinamic eligibilitatea pentru discount

### ❌ Probleme identificate

#### Problem 6: Lipsă Rate Limiting pe Webhook Endpoint
**Severitate**: MEDIE  
**Descriere**: `stripe_webhook()` nu are rate limiting sau protection.  
**Impactul**: Pot fi flood-uri de webhook calls fake.  
**Recomandare**: 
- Adaugati CSRF exempt dar validare de signature (deja faceți)
- Nu e necesar rate limiting pentru webhook (Stripe handle-ază) dar ar trebui logging pe abuse

#### Problem 7: Fără idempotency key handling
**Severitate**: MEDIE  
**Descriere**: Stripe API calls (Subscription.modify, etc.) nu au idempotency keys.  
**Impactul**: Dacă o request timeout-ează, retry-uri pot crea duplicate subscriptions.  
**Recomandare**: Adaugati `idempotency_key` parameter în Stripe API calls.

#### Problem 8: Manual VIP bypass nu e consistent
**Severitate**: JOASĂ  
**Descriere**: 
- `_is_manual_vip()` verifică `user.vip_manual_override`
- În views se numit `_is_manual_vip()` dar în webhook se verifică direct
**Recomandare**: Sempre using `_is_manual_vip()` helper pentru consistency.

#### Problem 9: Lipsă validation pe plan_tier input
**Severitate**: JOASĂ  
**Descriere**: 
```python
plan_tier = (request.data.get("plan_tier") or "premium").lower()
if plan_tier not in VALID_PLAN_TIERS:
    plan_tier = "premium"  # Silent fallback
```
**Impactul**: Dacă client trimite plan tier invalid, se defaultează la premium.  
**Recomandare**: 
```python
if plan_tier not in VALID_PLAN_TIERS:
    return Response({"detail": f"Invalid plan tier. Valid: {VALID_PLAN_TIERS}"}, 
                    status=status.HTTP_400_BAD_REQUEST)
```

---

## 4. Webhook Handler

### ✅ Aspect bun

- **Duplicate prevention**: `_register_webhook_event()` folosește event_id unic
- **Error tracking**: `_mark_webhook_failed()` loggează errors pentru debugging
- **Event types handled**:
  - `checkout.session.completed` → Activare plan
  - `customer.subscription.updated` → Sincronizare status + tier
  - `customer.subscription.deleted` → Downgrade la free/cancelled
  - `invoice.payment_failed` → Mark past_due + notification
  - `invoice.payment_succeeded` → Reactivate din past_due
  - `customer.source.expiring` → Notificare payment method
  - `charge.refunded` → Full refund handling

- **Notifications**: 
  - Payment expiring (7 days before period end)
  - Payment failed
  - Payment method invalid/expiring

- **User-friendly behavior**:
  - Nu downgrade manual VIP users
  - Track billing cycles
  - Handle past_due state

### ❌ Probleme identificate

#### Problem 10: Lipsă webhook event types
**Severitate**: MEDIE  
**Descriere**: Webhook handler nu procesează:
- `payment_intent.succeeded` (pentru one-time payments)
- `payment_intent.payment_failed`
- `customer.updated`

**Recomandare**: Documentati care event types sunt intentional ignore-uți.

#### Problem 11: Webhook retry logic incomplet
**Severitate**: MEDIE  
**Descriere**: 
```python
if created:
    return obj, True  # Process
else:
    # Update only delivery_attempts, mark as IGNORED
    return obj, False  # Don't process
```
**Impactul**: Dacă o request se pierde și Stripe retry-ează, nu se va reprocess.  
**Recomandare**: 
```python
# Re-process failed webhooks after N attempts
if obj.last_status == "failed" and obj.delivery_attempts < 3:
    return obj, True
```

#### Problem 12: Lipsă timeout handling pe Stripe API calls
**Severitate**: JOASĂ  
**Descriere**: Stripe API calls în webhook nu au timeout protecție.  
**Recomandare**: Wrappati în try-except cu timeout errors.

#### Problem 13: Error logging la SystemErrorEvent nu e mandatory
**Severitate**: JOASĂ  
**Descriere**: 
```python
try:
    SystemErrorEvent.objects.create(...)
except Exception:
    return  # Silent fail
```
**Recomandare**: Cel puțin log-ati la stderr dacă error creation fails.

---

## 5. Management Commands

### ✅ Aspect bun

- **sync_subscriptions**: 
  - Iterate cu `.iterator()` pentru memory efficiency
  - Status mapping corect
  - User-friendly output (checked, updated, failed counts)
  - Handles billing cycle dates
  - Respects manual VIP override

### ❌ Probleme identificate

#### Problem 14: Duplicat `_price_id_to_tier` în sync_subscriptions
(Deja mentionat în Problem 2)

#### Problem 15: Fără schedule pentru sync command
**Severitate**: MEDIE  
**Descriere**: `manage.py sync_subscriptions` trebuie executat manual.  
**Recomandare**: 
- Schedule-ati cu Celery/APScheduler să ruleze zilnic
- Și-o integrare posibilă în `PlatformScheduledJob` model

---

## 6. Admin Interface

### ✅ Aspect bun

- **PaymentAdmin**:
  - List display relevant
  - Sortare și filtering
  - Autocomplete pe user
  - Audit trail (via `log_admin_change`)

- **StripeWebhookEventAdmin**:
  - Read-only fields să previne modificări accidentale
  - Payload preview helper
  - Ordering by recency

### ❌ Probleme identificate

#### Problem 16: StripeConfigAdmin nu arată Product IDs
**Severitate**: MEDIE  
**Descriere**: 
```python
@admin.register(StripeConfig)
class StripeConfigAdmin(SingletonProxyConfigAdmin):
    fieldsets = (
        ("Stripe", {
            "fields": (
                "stripe_secret_key",
                "stripe_webhook_secret",
                "stripe_price_id_premium",
                # Missing: stripe_product_id_basic, etc.
```

**Recomandare**: Adaugati product ID fields și update StripeConfigAdminForm masked_fields.

#### Problem 17: Lipsă "Test Stripe Connection" button
**Severitate**: JOASĂ  
**Descriere**: Admin interface nu are test endpoint pentru validare Stripe config.  
**Recomandare**: Adaugati custom admin action care să testeze:
```python
def test_stripe_connection(self, request, queryset):
    try:
        stripe.Account.retrieve()
        self.message_user(request, "✓ Stripe connected successfully")
    except Exception as e:
        self.message_user(request, f"✗ Stripe error: {e}", level=messages.ERROR)
```

---

## 7. Testing

### ✅ Aspect bun
- Teste pentru early discount aplicabil
- Teste pentru fallback la internal activation

### ❌ Probleme identificate

#### Problem 18: Lipsă Integration Tests
**Severitate**: MEDIE  
**Descriere**: 
- Fără teste pentru webhook signature validation
- Fără teste pentru refund flow
- Fără teste pentru subscription modification
- Fără teste pentru edge cases (past_due → active → cancelled)

**Recomandare**: Adaugati pytest fixtures cu mock Stripe API:
```python
@pytest.fixture
def mock_stripe():
    with patch('stripe.checkout.Session.create') as mock:
        yield mock

def test_stripe_webhook_checkout_completed(mock_stripe, user):
    # Test webhook processing
```

#### Problem 19: Lipsă test pentru rate limiting
**Severitate**: JOASĂ  
**Descriere**: Throttle classes sunt testate?  
**Recomandare**: Adaugati throttle bypass test și rate limit test.

---

## 8. Documentation și Transparency

### ✅ Aspect bun
- Frontend are pagina de legal pentru Stripe disclosures

### ❌ Probleme identificate

#### Problem 20: Lipsă dev documentation
**Severitate**: JOASĂ  
**Descriere**: 
- Nu e documentat cum să se setup Stripe testing mode local
- Nu e clar care sunt exact price ID vs product ID diferentele
- Nu e clar care webhook events sunt handled

**Recomandare**: Creati `STRIPE_SETUP.md` cu:
```markdown
# Stripe Setup Guide

## Local Testing
1. Create Stripe test account
2. Set STRIPE_SECRET_KEY to sk_test_...
3. Test webhooks with `stripe listen --forward-to`

## Product IDs vs Price IDs
- Product IDs: prod_...
- Price IDs: price_... (recommended for subscriptions)
- Current system uses: Price IDs

## Webhook Testing
stripe trigger invoice.payment_failed
```

---

## 9. Security Considerations

### ✅ Aspect bun
- Webhook signature verification cu `stripe.Webhook.construct_event()`
- Sensitive fields masked în admin (PasswordInput)
- Customer data stored separately în Stripe (PCI compliance)
- No storing de credit card details local

### ❌ Probleme identificate

#### Problem 21: Nicio encryption pentru Stripe secrets în DB
**Severitate**: MEDIE  
**Descriere**: `stripe_secret_key` stocat plain text în `SystemConfig.stripe_secret_key`  
**Impactul**: Dacă DB e compromised, Stripe key e exposed.  
**Recomandare**: 
- Folositi Django's `get_secret()` cu encryption
- Sau stocati secrets only în environment variables
- Sau folositi AWS Secrets Manager/HashiCorp Vault

#### Problem 22: Lipsă PII logging protection
**Severitate**: MEDIE  
**Descriere**: Webhook payload se stochează în `StripeWebhookEvent.payload` - poate conține PII  
**Recomandare**: 
```python
payload = event.get("data", {}).get("object", {})
# Sanitize before storing
safe_payload = {k: v for k, v in payload.items() 
                if k not in ['card', 'email', 'phone']}
```

---

## 10. Observations & Recommendations

### Quick Wins (low effort, high impact)

1. **Refactorizati `_price_id_to_tier` în system_config.py**
   - Timp: 30 min
   - Impact: Better code maintainability

2. **Adaugati StripeConfigAdmin product ID fields**
   - Timp: 15 min
   - Impact: Complete admin interface

3. **Adaugati validation error pe invalid plan_tier**
   - Timp: 10 min
   - Impact: Better API error messages

### Medium Priority (1-2 ore)

4. **Add API request idempotency keys**
   - Implement pentru Subscription.modify(), create(), etc.
   
5. **Adaugati retry logic pentru failed webhooks**
   - Allow reprocessing failed events

6. **Create STRIPE_SETUP.md documentation**
   - Help future developers understand system

### Major Items (4-8 ore)

7. **Product ID vs Price ID decision**
   - Document final decision
   - Implement Product ID support completely

8. **Add comprehensive integration tests**
   - Webhook handling
   - Refund flows
   - Edge cases

9. **Encryption pentru Stripe secrets**
   - Implement Django secrets or env-only approach
   - Migrate existing secrets

10. **Implement webhook event retry scheduling**
    - Use Celery/APScheduler para scheduled sync

---

## 11. Compliance Checklist

- ✅ Webhook signature verification
- ✅ Status synchronization
- ✅ Billing cycle tracking
- ❌ PII storage in webhook events (GDPR risk)
- ❌ Secrets encryption in database
- ✅ Payment status audit trail
- ⚠️ Incomplete error handling (missing event types)

---

## Concluzie

**Sistemul Stripe este functional pe 80%** dar necesită:
1. Code cleanup (unire duplicate functions)
2. Admin interface completare
3. Error handling improvements
4. Security enhancements (secrets, PII)
5. Testing expansion
6. Documentation

**Prioritate**: Fix Problems 2, 6, 11, 16, 18, 21, 22 înainte de production deployment.

**Timp estimat pentru fixuri**: 8-10 ore

