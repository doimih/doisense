# Step 8: AI Customer Support System Audit
**Status:** Completed  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Customer support infrastructure is **PARTIALLY IMPLEMENTED** but missing specialized AI routing:

- ✅ **Basic Contact Form** - Manual form submission with email routing
- ✅ **reCAPTCHA Protection** - Spam prevention enabled
- ✅ **Email Configuration** - SMTP support works
- ❌ **NO AI Support Routing** - Single general chat, no specialized agents
- ❌ **NO Account Support AI** - No bot for account questions
- ❌ **NO Billing/Subscription AI** - No bot for billing questions  
- ❌ **NO GDPR/Data AI** - No bot for privacy questions
- ❌ **NO Categorization** - All support requests treated equally
- ❌ **NO Ticketing System** - No tracking or responses

**Impact:** Support requests disappear into email, users get no AI assistance with common issues.

---

## 1. Current Implementation

### 1.1 Contact Form (Manual, Not AI-Assisted)

**Endpoint:** `POST /contact/submit` in `backend/core/views.py`

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "subject": "I need help with my account",
  "message": "I forgot my password and can't log in",
  "recaptcha_token": "..."
}
```

**Current Flow:**
1. User fills form on `/contact` page
2. Form validates inputs (name, email, subject, message)
3. reCAPTCHA validation optional (if enabled)
4. Email sent directly to admin (`config.contact_notification_email`)
5. Admin responds manually (or doesn't)

**Issues:**
- ❌ No AI classifier to route to appropriate team
- ❌ No automated responses
- ❌ No ticket tracking (user can't follow up)
- ❌ No categorization (billing, technical, general, etc.)
- ❌ No status updates (user never knows it was received)
- ⚠️ reCAPTCHA configured but often misconfigured in production

**Status:** ⚠️ Basic but not SaaS-standard

---

### 1.2 Support Disclaimer in AI Chat

**File:** `backend/ai/prompt_builder.py`

```python
SUPPORT_DISCLAIMER = (
    "I'm an AI assistant, not a medical professional. "
    "If you're in crisis or need urgent help, please contact emergency services or a mental health professional."
)
```

**Current Feature:**
- Inserted into chat on every 10th message
- Also added when medical keywords detected (diagnose, suicide, panic attack, etc.)

**Issues:**
- ⚠️ Disclaimer about medical support, not account/billing support
- ❌ No routing to actual support for critical issues
- ❌ Doesn't help with account lockout, billing errors, or GDPR data requests

**Status:** ⚠️ One-way message, not actionable support

---

### 1.3 Administrator Email Configuration

**SystemConfig Model:** `backend/core/models.py`

```python
contact_notification_email = EmailField()  # Where to send support requests
contact_from_email = EmailField()          # Sender email

email_host = CharField()                   # SMTP host
email_host_user = CharField()              # SMTP username
email_host_password = CharField()          # SMTP password
email_port = IntegerField()                # SMTP port
email_use_tls = BooleanField()            # TLS enabled
email_use_ssl = BooleanField()            # SSL enabled
```

**Issues:**
- ✅ Flexible email configuration
- ❌ All support goes to single email
- ❌ No agent routing
- ❌ No automation

**Status:** ✅ Works but basic

---

## 2. What's Missing

### Gap 1: Account Support AI

**Missing:** Dedicated AI agent for account-related questions

**Example Questions:**
- "How do I reset my password?"
- "How do I change my email address?"
- "How do I enable two-factor authentication?"
- "Can I change my username?"
- "How do I download my data?"

**Implementation:** Create `AccountSupportAgent`

---

### Gap 2: Subscription Support AI

**Missing:** Dedicated AI agent for subscription and trial questions

**Example Questions:**
- "When will my trial expire?"
- "How do I upgrade to Premium?"
- "How do I cancel my subscription?"
- "What's included in Premium?"
- "Can I switch from Basic to Premium?"

**Implementation:** Create `SubscriptionSupportAgent`

---

### Gap 3: Billing Support AI

**Missing:** Dedicated AI agent for invoice and payment questions

**Example Questions:**
- "Where's my invoice?"
- "Why was I charged twice?"
- "Do you offer refunds?"
- "How do I update my payment method?"
- "What's your refund policy?"

**Implementation:** Create `BillingSupport Agent`

---

### Gap 4: GDPR/Privacy Support AI

**Missing:** Dedicated AI agent for privacy and data requests

**Example Questions:**
- "How do you store my data?"
- "What's your privacy policy?"
- "Can I request my data?"
- "How do I delete my account?"
- "Is my data encrypted?"
- "Do you sell my data?"
- "How long do you keep my data?"

**Implementation:** Create `GDPRSupportAgent`

---

### Gap 5: Categorization & Routing

**Missing:** System to detect question type and route to correct agent

**Needed:**
```python
class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('account', 'Account Issues'),
        ('subscription', 'Subscription/Trial'),
        ('billing', 'Billing/Invoices'),
        ('gdpr', 'Privacy/Data'),
        ('feature', 'Feature Requests'),
        ('bug', 'Bug Report'),
        ('general', 'General Question'),
    ]
    
    user = ForeignKey(User)
    category = CharField(choices=CATEGORY_CHOICES)
    title = CharField()
    description = TextField()
    ai_response = TextField()  # AI-generated first response
    status = CharField(['open', 'resolved', 'escalated'])
    created_at = DateTimeField(auto_now_add=True)
```

---

## 3. Recommended Implementation Plan

### Phase 1: Ticket System & Categorization (1 week)

**1.1 Create Support Ticket Model**
```python
class SupportTicket(models.Model):
    # Unique for tracking
    ticket_id = CharField(unique=True, default=generate_ticket_id)  # e.g., SUP-20260311-001
    
    # User & contact info
    user = ForeignKey(User, null=True)
    user_email = EmailField()
    
    # Content
    category = CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = CharField(max_length=200)
    description = TextField()
    
    # AI Response
    ai_response = TextField(blank=True)
    ai_model_used = CharField(blank=True)  # e.g., 'gpt-4', 'claude'
    
    # Status
    status = CharField(max_length=20, choices=[...])
    priority = CharField(max_length=20, choices=[...])
    
    # Tracking
    created_at = DateTimeField(auto_now_add=True)
    resolved_at = DateTimeField(null=True)
    human_escalated_at = DateTimeField(null=True)
```

**1.2 Create Categorization AI**
```python
def categorize_support_request(message: str) -> str:
    """
    Use AI to detect category:
    - 'account' if mentions: password, email, username, two-factor, download data
    - 'subscription' if mentions: trial, upgrade, downgrade, premium
    - 'billing' if mentions: invoice, charge, payment, refund
    - 'gdpr' if mentions: data, privacy, delete account, encryption
    - 'feature' if mentions: feature, enhancement, idea, suggestion
    - 'bug' if mentions: error, broken, doesn't work, crash
    - 'general' default
    """
    prompt = f"""Categorize this support request:
{message}

Choose exactly one category:
- account (password reset, email change, 2FA, download data)
- subscription (trial, upgrade/downgrade, cancellation)
- billing (invoice, payment, refund, charge issues)
- gdpr (privacy, data requests, account deletion)
- feature (feature request, enhancement)
- bug (error, broken feature, crash)
- general (other)

Respond with ONLY the category name."""
    
    response = client.chat.completions.create(
        model="gpt-4-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().lower()
```

**Effort:** ~20 hours

---

### Phase 2: Support Agents (2 weeks)

**2.1 Account Support Agent**
```python
def auto_response_account(ticket: SupportTicket) -> str:
    """Generate response for account-related issues"""
    prompt = f"""The user asked about their account:

{ticket.description}

Provide a helpful response covering:
1. Answer their specific question
2. Link to account settings page
3. Offer escalation if needed

Be concise and friendly. Do NOT make account changes directly."""
    
    return generate_response(prompt)
```

**2.2 Subscription Support Agent**
```python
def auto_response_subscription(ticket: SupportTicket, user: User) -> str:
    """Generate response for subscription issues"""
    prompt = f"""The user asked about their subscription:

{ticket.description}

Their current plan: {user.plan_tier}
Trial ends: {user.trial_ends_at}
Subscription status: {get_payment_status(user)}

Provide helpful info about their current plan, upgrade options,
and answer their specific question."""
    
    return generate_response(prompt)
```

**2.3 Billing Support Agent**
```python
def auto_response_billing(ticket: SupportTicket, user: User) -> str:
    """Generate response for billing issues"""
    prompt = f"""The user asked about billing:

{ticket.description}

Their recent charges:
{get_user_invoices(user)}

Provide invoice info, explain charges, explain options
(refunds, cancellation, etc.)"""
    
    return generate_response(prompt)
```

**2.4 GDPR Support Agent**
```python
def auto_response_gdpr(ticket: SupportTicket, user: User) -> str:
    """Generate response for privacy/GDPR requests"""
    prompt = f"""The user asked about privacy/GDPR:

{ticket.description}

Provide information about:
- How their data is stored and protected
- Privacy policy details
- Data download/deletion procedures
- Processing times
- Contact info for formal requests"""
    
    return generate_response(prompt)
```

**Effort:** ~40 hours (8 hours per agent + integration)

---

### Phase 3: Full Ticketing & Escalation (1 week)

**3.1 Ticket Management UI (Admin)**
- List all open tickets
- Filter by category, status, priority
- View AI response + manual notes
- Mark as resolved/escalated
- Send follow-up messages

**3.2 User Tracking**
- Users can see their ticket history
- Push notifications when resolved
- Email confirmations

**3.3 Escalation Rules**
```python
def should_escalate(ticket: SupportTicket) -> bool:
    # Escalate if:
    # - User explicitly requests human support
    # - Sensitivity: mentions legal, criticism, GDPR formal request
    # - Complex: involves account modifications needed
    # - Urgent: mentions crisis, security breach
    
    keywords_critical = ['suicide', 'emergency', 'hacked', 'breach']
    if any(kw in ticket.description.lower() for kw in keywords_critical):
        return True
    
    keywords_gdpr_formal = ['formal request', 'under gdpr article', 'data subject']
    if any(kw in ticket.description.lower() for kw in keywords_gdpr_formal):
        return True
    
    return False
```

**Effort:** ~30 hours

---

## 4. API Endpoints

### New Endpoints Needed

**POST /support/tickets** - Create support request
```
Request:
{
  "subject": "I forgot my password",
  "description": "I can't reset it via email link",
  "category": "account"  // optional, AI will categorize
}

Response:
{
  "ticket_id": "SUP-20260311-001",
  "subject": "...",
  "category": "account",
  "ai_response": "Here's how to reset your password...",
  "status": "open",
  "created_at": "2026-03-11T10:00:00Z"
}
```

**GET /support/tickets/{ticket_id}** - Track existing request
```
{
  "ticket_id": "SUP-20260311-001",
  "status": "resolved",
  "created_at": "...",
  "resolved_at": "...",
  "ai_response": "...",
  "admin_notes": "Password reset sent successfully"
}
```

**GET /support/tickets/my-tickets** - List user's tickets
```
[
  {
    "ticket_id": "SUP-...",
    "subject": "...",
    "status": "open",
    "created_at": "..."
  }
]
```

---

## 5. Database Schema

```sql
CREATE TABLE core_supportticket (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE,
    user_id INTEGER REFERENCES users_user(id),
    user_email VARCHAR(254),
    category VARCHAR(20),
    subject VARCHAR(200),
    description TEXT,
    ai_response TEXT,
    ai_model_used VARCHAR(50),
    status VARCHAR(20),  -- open, resolved, escalated
    priority VARCHAR(20),  -- low, medium, high, urgent
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP NULL,
    human_escalated_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ticket_user ON core_supportticket(user_id);
CREATE INDEX idx_ticket_status ON core_supportticket(status);
CREATE INDEX idx_ticket_category ON core_supportticket(category);
```

---

## 6. Frontend Integration

### Support Page Changes

**Current:** Contact form only  
**New:** Three-tab interface:
1. **Submit Ticket Tab** - Form to submit new request
2. **Track Ticket Tab** - Enter ticket ID to check status
3. **My Tickets Tab** (if logged in) - View all own tickets

```vue
<template>
  <div class="max-w-2xl mx-auto">
    <Tabs>
      <Tab label="New Ticket">
        <SupportForm />
      </Tab>
      <Tab label="Track Ticket">
        <TrackTicketForm />
      </Tab>
      <Tab v-if="authStore.isLoggedIn" label="My Tickets">
        <MyTicketsList />
      </Tab>
    </Tabs>
  </div>
</template>
```

---

## 7. Success Metrics

After implementation:

| Metric | Current | Target |
|--------|---------|--------|
| Support request response time | Manual (hours/days) | AI (immediate) + human (24h) |
| Self-service resolution rate | 0% | 70% (AI handles 7/10) |
| Ticket tracking available | ❌ | ✅ 100% |
| Category accuracy | N/A | 95%+ |
| User satisfaction (CSAT) | Unknown | 4.5/5 stars |
| Time to resolve | N/A | < 2 hours (AI) or escalated to human |

---

## 8. Files to Create/Modify

**Backend:**
- [ ] `backend/core/models.py` - Add `SupportTicket` model
- [ ] `backend/core/views.py` - Add ticket endpoints
- [ ] `backend/core/support_agents.py` - New file with 4 agents
- [ ] `backend/core/categorizer.py` - New file with categorization logic
- [ ] `backend/core/admin.py` - Admin interface for tickets
- [ ] `backend/core/migrations/` - Create migration

**Frontend:**
- [ ] `frontend/pages/support/index.vue` - Update contact page
- [ ] `frontend/pages/support/[ticket_id].vue` - Ticket tracking

**Tests:**
- [ ] `backend/core/tests/test_support.py` - Full test coverage

---

## Next Steps

1. ✅ Audit complete
2. ❓ Approve Phase 1 (ticket system)
3. ❓ Approve Phase 2 (support agents)
4. ❓ Start implementation

---
