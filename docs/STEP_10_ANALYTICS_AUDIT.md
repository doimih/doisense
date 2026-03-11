# Step 10: Product Analytics Dashboard Audit
**Status:** Completed  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

Analytics dashboards are **PARTIALLY IMPLEMENTED**:

- ✅ **Admin Dashboard Exists** - 8 core metrics (users, conversions, activity)
- ✅ **GDPR Consent Framework** - Tracks user analytics preferences
- ✅ **Backend Logging** - Conversations, AI logs, emotions recorded
- ❌ **Active/Inactive Segmentation** - Missing user engagement buckets
- ❌ **Trial → Premium Conversion** - No conversion funnel tracking
- ❌ **Retention Analysis** - Can't measure user cohort retention
- ❌ **Churn Metrics** - Missing churn rate calculations
- ❌ **Upgrade/Downgrade Tracking** - No plan change history
- ❌ **Revenue Dashboard** - Zero financial analytics
- ❌ **AI Engagement Metrics** - Missing conversation analytics
- ❌ **Dominant Emotions** - Emotions stored but not analyzed/displayed
- ❌ **User Progress Tracking** - Program completion not visible
- ❌ **GDPR Requests Dashboard** - No tracking for data requests/deletions

**Impact:** Business can't measure product-market fit, can't identify at-risk users, can't optimize monetization.

**Risk Level:** 🟡 **HIGH** - Data exists but can't be acted upon

---

## 1. Current Implementation

### 1.1 Admin Dashboard (Partial)

**Location:** `backend/core/admin_dashboard.py` + `backend/templates/admin/index.html`

**Current Metrics (8 total):**
```
✅ Total Users
   - Count: total user accounts created
   - Trend: new users added per day (7/30/90 day view)

✅ Premium Users  
   - Count: users with is_premium=True
   - Rate: percentage of total users converting to premium
   - Trend: premium conversion cumulative %

✅ New Users (30d)
   - Count: users created in last 30 days
   
✅ Active Subscriptions
   - Count: payments with status = 'active' or 'trialing'
   
✅ Active Users (7d)
   - Count: distinct users with journal entries OR AI logs in 7 days
   
✅ Journal Entries
   - Total count across all users
   - Daily trend chart (7/30/90 day view)
   
✅ AI Logs
   - Total count across all users

✅ Top Languages
   - Distribution of users by language
   - Shows top 5 languages as progress bars
```

**Data Points Shown:**
- Total users trend (line chart)
- Journal entries trend (bar chart)
- Premium conversion trend (cumulative %)
- Language distribution (progress bars)
- Selectable period filters (7d, 30d, 90d)

**Access:** Django admin only (`/admin/`)  
**Audience:** Internal team only  
**Status:** ⚠️ Basic but limited

---

### 1.2 Models with Analytics Data

**User Model** (`users.models.User`)
```python
✅ plan_tier: free|trial|basic|premium|vip
✅ is_premium: boolean
✅ created_at: datetime
✅ trial_started_at: datetime
✅ trial_ends_at: datetime
✅ onboarding_completed: boolean  (can measure onboarding conversion)
```

**Conversation Model** (`ai.models.Conversation`)
```python
✅ user_id: FK to User
✅ module: type of conversation
✅ plan_tier: user's tier at time of conversation
✅ created_at: datetime
```

**JournalEntry Model** (`journal.models.JournalEntry`)
```python
✅ user_id: FK to User
✅ question_id: FK to JournalQuestion
✅ emotions: JSONField (stores emotion data!)  ← Can be analyzed
✅ created_at: datetime
```

**Payment Model** (`payments.models.Payment`)
```python
✅ user_id: FK to User
✅ plan_tier: basic|premium|vip
✅ status: active|cancelled|past_due|trialing
✅ created_at: when subscription started
✅ updated_at: when status changed
```

**AILog Model** (`ai.models.AILog`)
```python
✅ user_id: FK to User
✅ model: AI model used (gpt-4, claude, etc.)
✅ created_at: datetime
```

**Status:** ✅ Data exists to build requested dashboards

---

## 2. What's Missing

### Gap 1: Active/Inactive User Segmentation

**Current State:**
- ✅ "Active users (7d)" metric exists (based on journal/AI activity)
- ❌ No inactive user segmentation
- ❌ No multi-tier activity analysis (DAU, WAU, MAU)

**Missing Metrics:**
```
Daily Active Users (DAU)
  - Unique users with activity in last 24 hours
  - Trend over time
  
Weekly Active Users (WAU)
  - Unique users with activity in last 7 days
  - Trend over time
  
Monthly Active Users (MAU)
  - Unique users with activity in last 30 days
  - Trend over time
  
Active / Inactive Breakdown
  - Users active in last 7 days
  - Users active in last 30 days but not 7
  - Users inactive > 30 days
  - Activity defined as: journal entry OR AI conversation
  
Engagement Tiers
  - Super Active: 3+ actions per week
  - Active: 1-2 actions per week
  - At Risk: No action in 2+ weeks
  - Churned: No action in 30+ days
```

**Implementation:** Requires activity event aggregation

---

### Gap 2: Trial → Premium Conversion Funnel

**Current State:**
- ✅ Overall conversion rate exists (premium users / total users)
- ❌ No trial-specific conversion tracking
- ❌ No conversion funnel by stage
- ❌ No time-to-conversion metrics

**Missing Metrics:**
```
Trial Funnel (from signup to payment):
  1. Signup complete (100%)
  2. Onboarding started (X%)
  3. Onboarding completed (X%)
  4. First chat/journal (X%)
  5. Trial expiring notification sent (X%)
  6. Upgrade attempted (X%)
  7. Payment successful (X%)
  
Trial Performance:
  - Total users in trial: X
  - Converted to premium: X (Y%)
  - Converted to basic: X (Y%)
  - Churned (trial expired): X (Y%)
  
Time-to-Conversion:
  - Median days from signup to first payment
  - Distribution histogram
  - Variation by cohort (signup week/month)
```

**Implementation:** Requires trial event tracking and conversion funnel model

---

### Gap 3: Retention Curves by Cohort

**Current State:**
- ❌ Zero retention tracking
- ❌ No cohort analysis
- ❌ Can't measure if users come back

**Missing Metrics:**
```
Retention Cohort Table (by signup week):
        Week 0  Week 1  Week 2  Week 4  Week 8
Jan 1     100%    65%     48%     32%     18%
Jan 8      100%    70%     52%     35%     20%
Jan 15     100%    68%     50%     33%     19%
(Shows % of cohort still active)

Day 1, Day 7, Day 30 Retention
  - What % open on day 1 after signup?
  - What % open at least once in first week?
  - What % open at least once in first month?

Rolling Retention
  - Each week's cohort retention curve
  - Identify if retention improving/declining
```

**Implementation:** Requires UserActivity or engagement event table

---

### Gap 4: Churn Analysis

**Current State:**
- ❌ No churn metrics
- ❌ No churn prediction
- ❌ No churn reason tracking

**Missing Metrics:**
```
Churn Rate (Monthly)
  - Users who had activity in month N-1 but not month N
  - Calculate by plan tier (basic churn vs premium churn)
  - Calculate by region/language
  
Churn Reasons
  - Canceled subscription reason
  - Survey: "Why are you leaving?"
  - Predictors: (low engagement, high errors, feature requests unanswered)
  
Churn Risk Cohort
  - Users with declining activity trend
  - Users with support tickets/complaints
  - Users on trial near expiration
  - Users who haven't converted after 6 days trial
```

**Implementation:** Requires UserActivity aggregation + CancellationReason model

---

### Gap 5: Upgrade / Downgrade Tracking

**Current State:**
- ✅ Payment records exist
- ❌ No plan change history
- ❌ No upgrade/downgrade metrics

**Missing Metrics:**
```
Plan Changes:
  - Users who upgraded: free → trial/basic/premium/vip
  - Users who downgraded: premium → basic, etc.
  - Timing: when did they upgrade? (days from signup)
  - Win-back: users who canceled then re-subscribed
  
Upgrade Conversion:
  - % of basic users who upgrade to premium
  - Days between signup and upgrade
  - Feature triggers for upgrade (journal limit hit, chat limit hit)
  
Downgrade Patterns:
  - When do premium users downgrade?
  - To which tier?
  - What's the churn risk 30 days after downgrade?
```

**Implementation:** Requires PaymentHistory or tracking plan_tier changes

---

### Gap 6: Revenue Metrics Dashboard

**Current State:**
- ❌ No revenue tracking at all
- ✅ Payment records exist in DB
- ❌ No dashboard to see financial data

**Missing Metrics:**
```
Revenue Overview:
  - MRR (Monthly Recurring Revenue) by plan
  - ARR (Annual Recurring Revenue) estimate
  - ARPU (Average Revenue Per User)
  - Total active subscription value
  
Customer Metrics:
  - Paying customers count
  - Paying vs free ratio
  - Revenue per customer (lifetime + MRR)
  
Revenue Cohort Analysis:
  - Revenue contribution by signup cohort
  - Revenue retention (do cohorts keep paying?)
  - LTV (Lifetime Value) by cohort
  
Plan Distribution:
  - % customers on basic vs premium vs vip
  - Revenue contribution by plan
  - Plan mix over time
```

**Status:** 🔴 CRITICAL - No financial visibility

---

### Gap 7: AI Engagement Metrics

**Current State:**
- ❌ No engagement analysis
- ✅ Conversation records exist
- ✅ AILog records exist

**Missing Metrics:**
```
Chat Engagement:
  - Total conversations (all time)
  - Conversations per user (avg, median, distribution)
  - Conversation frequency (daily, weekly, monthly)
  - Active chat users (7d, 30d, 90d)
  
Chat Depth:
  - Users with 1-5 conversations
  - Users with 5-20 conversations
  - Users with 20+ conversations
  - Conversion rate by depth bracket
  
Conversation Quality:
  - Avg conversation length (tokens)
  - Most common conversation topics/modules
  - How often do users continue a conversation?
  
AI Feature Usage:
  - Monthly AI feature distribution (chat vs journal analysis vs etc)
  - Power users (top 10% of AI users)
  - AI usage by plan tier
  
AI Adoption:
  - % of users who ever used chat
  - % of active users who use AI weekly
  - Feature flag adoption (if A/B testing exists)
```

**Implementation:** Requires Conversation analysis queries

---

### Gap 8: Dominant Emotions Analysis

**Current State:**
- ✅ Emotions stored in JournalEntry.emotions (JSONField)
- ❌ No visualization of emotion data
- ❌ No emotion trends analysis
- ❌ No emotion analytics views

**Missing Metrics:**
```
Most Common Emotions (across platform):
  - Emotion frequency distribution (pie/bar chart)
  - Trend over time (are users getting happier?)
  
Emotion Trends by User:
  - Individual user's emotion journey over time
  - Are they improving?
  
Emotion by Feature:
  - Emotions in journal entries (tracked by emotion field)
  - Emotions reported in AI conversations (could extract via NLP)
  
Emotional Health Segments:
  - Users mostly positive emotions (70%+ positive)
  - Users mixed emotions (40-60% positive)
  - Users mostly negative emotions (<40% positive)
  - Alert users showing severe distress (for crisis support)
```

**Implementation:** Requires emotion aggregation and visualization

---

### Gap 9: User Progress Tracking

**Current State:**
- ❌ No progress dashboard
- ✅ GuidedProgram and GuidedProgramDay models exist (from Step 7)
- ❌ No UserProgramEnrollment model yet (needed for progress)
- ❌ No completion tracking

**Missing Metrics:**
```
Program Engagement:
  - Users who started a program
  - Users who completed a program
  - Completion rate (%)
  - Avg days to complete
  
Program Performance:
  - Programs with highest adoption
  - Programs with highest completion rate
  - Programs with highest engagement (time spent)
  
User Progress:
  - Per user: which programs enrolled in
  - Per program: current day user is on
  - Streak tracking (consecutive days completed)
  - Days since last activity in program
  
Program Funnel:
  - Users who viewed program details
  - Users who enrolled
  - Users who completed day 1
  - Users who completed day 7
  - Users who completed all days
  
Milestone Tracking:
  - Day 7 completion
  - Day 14 completion
  - Full program completion
```

**Status:** ⚠️ Requires Step 7 completion first (UserProgramEnrollment model)

---

### Gap 10: GDPR Requests Dashboard

**Current State:**
- ❌ No GDPR request tracking
- ❌ No compliance dashboard
- ✅ Data deletion implemented (backend logic exists)

**Missing Metrics:**
```
GDPR Requests (Admin View):
  - Total data deletion requests
  - Total data export requests
  - Total consent withdrawal requests
  
GDPR Compliance:
  - Requests pending (by age: <7 days, <30 days)
  - Requests completed (count, avg completion time)
  - Requests rejected (with reason)
  - SLA compliance (GDPR requires 30-day response: X% on-time)
  
Data Subject Rights:
  - Export requests: format options selected (JSON, CSV, etc)
  - Deletion requests: reason provided (if captured)
  - Scope requested (all data vs specific entities)
  
Audit Trail:
  - Who processed each request?
  - When was it completed?
  - What data was deleted/exported?
  - Proof of completion (logged for compliance)
```

**Implementation:** Requires GDPRRequest model + compliance tracking

---

## 3. Recommended Implementation Plan

### Phase 1: Extend Existing Dashboard (2 weeks)
**Priority: HIGH**

#### 1.1 Add Engagement Metrics

**New Card Components:**
- DAU, WAU, MAU metrics
- Engagement tier breakdown (super active, active, at-risk, churned)
- Active/inactive user count

**Effort:** 8 hours

```python
# backend/core/admin_dashboard.py - Add:

def get_engagement_tiers():
    """Segment users by activity in last 30 days"""
    today = timezone.localdate()
    start_30d = timezone.now() - timedelta(days=30)
    start_14d = timezone.now() - timedelta(days=14)
    start_7d = timezone.now() - timedelta(days=7)
    
    # Users with activity
    last_7d_active = User.objects.filter(
        Q(journal_entries__created_at__gte=start_7d) |
        Q(conversations__created_at__gte=start_7d)
    ).distinct()
    
    last_14d_active = User.objects.filter(
        Q(journal_entries__created_at__gte=start_14d) |
        Q(conversations__created_at__gte=start_14d)
    ).distinct()
    
    last_30d_active = User.objects.filter(
        Q(journal_entries__created_at__gte=start_30d) |
        Q(conversations__created_at__gte=start_30d)
    ).distinct()
    
    return {
        'dau': last_7d_active.count() / 7,  # Rough daily estimate
        'wau': last_7d_active.count(),
        'mau': last_30d_active.count(),
        'active': last_7d_active.count(),
        'at_risk': last_30d_active.exclude(
            id__in=last_7d_active
        ).count(),
        'churned': User.objects.exclude(
            id__in=last_30d_active
        ).count(),
    }
```

---

#### 1.2 Add Revenue Metrics

**New Cards:**
- Active subscription count (already exists, rename)
- MRR estimate
- Paying vs free ratio

**Effort:** 6 hours

```python
# Add to admin_dashboard.py:

def get_revenue_metrics():
    """Calculate basic revenue metrics"""
    today = timezone.localdate()
    
    # Active subscriptions
    active_subs = Payment.objects.filter(
        status__in=['active', 'trialing']
    ).count()
    
    # Basic estimate: assume each is $10/month (or get from Stripe)
    # Note: Real implementation needs actual Stripe pricing
    estimated_mrr = active_subs * 10
    
    # Paying vs free
    paying_users = User.objects.filter(
        payments__status__in=['active', 'trialing', 'cancelled']
    ).distinct().count()
    
    free_users = User.objects.exclude(
        payments__status__in=['active', 'trialing', 'cancelled']
    ).count()
    
    return {
        'active_subscriptions': active_subs,
        'estimated_mrr': estimated_mrr,
        'paying_users': paying_users,
        'free_users': free_users,
        'paying_ratio': round(
            (paying_users / (paying_users + free_users)) * 100
        ) if (paying_users + free_users) > 0 else 0,
    }
```

---

#### 1.3 Add Emotion Analytics

**New Card:**
- Top emotions distribution
- Emotion trend over time

**Effort:** 8 hours

```python
# Add to admin_dashboard.py:

from collections import Counter

def get_emotion_analytics(days=30):
    """Analyze journal entry emotions"""
    today = timezone.localdate()
    start_date = today - timedelta(days=days)
    
    entries = JournalEntry.objects.filter(
        created_at__date__gte=start_date
    )
    
    # Flatten emotions from all entries
    all_emotions = []
    for entry in entries:
        if entry.emotions and isinstance(entry.emotions, list):
            all_emotions.extend(entry.emotions)
    
    # Count frequency
    emotion_counts = Counter(all_emotions)
    top_emotions = emotion_counts.most_common(5)
    
    return {
        'top_emotions': top_emotions,  # [(emotion, count), ...]
        'total_emotion_logs': len(all_emotions),
        'unique_emotions': len(emotion_counts),
        'trend': get_emotion_trend(days),  # Chart data
    }
```

**Status:** ⚠️ Requires parsing stored emotions format

---

### Phase 2: Create Analytics Models (3 weeks)

#### 2.1 UserActivity Model

```python
# backend/core/models.py or new file

class UserActivity(models.Model):
    """Track user engagement events for analytics"""
    ACTIVITY_TYPE_CHOICES = [
        ('journal_entry', 'Journal Entry'),
        ('ai_conversation', 'AI Conversation'),
        ('program_day_view', 'Program Day View'),
        ('program_day_complete', 'Program Day Completed'),
        ('payment_attempt', 'Payment Attempt'),
        ('support_ticket', 'Support Ticket'),
        ('onboarding_step', 'Onboarding Step'),
    ]
    
    user = ForeignKey(User, on_delete=models.CASCADE)
    activity_type = CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    metadata = JSONField(default=dict, blank=True)  # Extra data
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            Index(fields=['user', 'created_at']),
            Index(fields=['activity_type', 'created_at']),
        ]
```

**Usage:** Track events like journal entry, AI chat, program completion

---

#### 2.2 GDPRRequest Model

```python
class GDPRRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('export', 'Data Export'),
        ('deletion', 'Account Deletion'),
        ('rectification', 'Data Rectification'),
        ('restrict', 'Restrict Processing'),
        ('portability', 'Data Portability'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    user = ForeignKey(User, on_delete=models.CASCADE)
    request_type = CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    request_file = FileField(upload_to='gdpr_requests/', null=True, blank=True)
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Compliance tracking
    request_received_at = DateTimeField(auto_now_add=True)
    processing_started_at = DateTimeField(null=True, blank=True)
    completed_at = DateTimeField(null=True, blank=True)
    
    # Reason for deletion (optional, user self-reported)
    reason = CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-request_received_at']
```

---

#### 2.3 UserConversionFunnel Model

```python
class UserConversionFunnel(models.Model):
    """Track conversion through trial → premium"""
    STAGE_CHOICES = [
        ('signup', 'Signup Complete'),
        ('onboarding_start', 'Onboarding Started'),
        ('onboarding_complete', 'Onboarding Completed'),
        ('first_journal', 'First Journal Entry'),
        ('first_chat', 'First AI Chat'),
        ('trial_day_3', 'Trial Day 3+'),
        ('trial_day_7', 'Trial Day 7 (Expiring)'),
        ('payment_attempt', 'Payment Initiated'),
        ('payment_success', 'Payment Successful'),
        ('trial_expired', 'Trial Expired'),
    ]
    
    user = ForeignKey(User, on_delete=models.CASCADE)
    stage = CharField(max_length=30, choices=STAGE_CHOICES)
    reached_at = DateTimeField(auto_now_add=True)
    conversion_complete = BooleanField(default=False)  # Paid or not
    
    class Meta:
        ordering = ['-reached_at']
        unique_together = [('user', 'stage')]
```

**Effort:** 12 hours

---

#### 2.4 Cohort Analytics View

Create a denormalized view for cohort retention queries

```sql
-- backend/core/migrations - Add SQL fixture
CREATE VIEW cohort_retention AS
SELECT
  DATE_TRUNC('week', u.created_at)::date as signup_week,
  COUNT(DISTINCT u.id) as cohort_size,
  COUNT(DISTINCT CASE 
    WHEN je.created_at > u.created_at + INTERVAL '0 days'
    AND je.created_at < u.created_at + INTERVAL '1 days'
    THEN u.id
  END) as day_1_returned,
  COUNT(DISTINCT CASE 
    WHEN je.created_at > u.created_at + INTERVAL '6 days'
    AND je.created_at < u.created_at + INTERVAL '7 days'
    THEN u.id
  END) as day_7_returned,
  -- ... continue for day 30, etc
FROM users_user u
LEFT JOIN journal_journalentry je ON u.id = je.user_id
GROUP BY signup_week
ORDER BY signup_week DESC;
```

**Effort:** 8 hours

---

### Phase 3: Build Public Analytics Pages (3 weeks)

#### 3.1 Product Dashboard Endpoint

**New API Endpoint:** `GET /api/analytics/dashboard` (admin only)

```python
# backend/core/views.py / analytics.py

class AnalyticsDashboardView(APIView):
    """Admin-only analytics dashboard data"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        funnel = self._get_trial_conversion_funnel()
        retention = self._get_retention_cohort()
        churn = self._get_churn_metrics()
        revenue = self._get_revenue_metrics()
        emotions = self._get_emotion_trends()
        engagement = self._get_engagement_tiers()
        
        return Response({
            'funnel': funnel,
            'retention': retention,
            'churn': churn,
            'revenue': revenue,
            'emotions': emotions,
            'engagement': engagement,
        })
```

**Effort:** 16 hours

---

#### 3.2 Frontend Dashboard Components

**New Vue Components:**

```
components/
  analytics/
    EngagementCard.vue       # DAU/WAU/MAU
    RevenueCard.vue          # MRR, ARPU
    ConversionFunnelChart.vue
    RetentionCohortTable.vue
    ChurnMetricsCard.vue
    EmotionTrendChart.vue
    UserProgressCard.vue
    GDPRComplianceCard.vue
```

**Effort:** 20 hours

---

### Phase 4: GDPR & Compliance Features (2 weeks)

#### 4.1 GDPR Request Handling

```python
# backend/core/views.py - Add endpoint

class GDPRRequestCreateView(APIView):
    """User can request data export or deletion"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request_type = request.data.get('type')  # export|deletion
        reason = request.data.get('reason', '')
        
        gdpr_request = GDPRRequest.objects.create(
            user=request.user,
            request_type=request_type,
            reason=reason,
            status='pending'
        )
        
        # Trigger async task to process
        process_gdpr_request.delay(gdpr_request.id)
        
        return Response({'request_id': gdpr_request.id})
```

**Effort:** 12 hours

---

#### 4.2 Compliance Report

Create admin view showing GDPR metrics

```python
# backend/core/admin_dashboard.py - Add

def get_gdpr_metrics():
    """GDPR compliance dashboard"""
    today = timezone.now()
    
    # Requests overview
    total_requests = GDPRRequest.objects.count()
    pending = GDPRRequest.objects.filter(status='pending').count()
    completed = GDPRRequest.objects.filter(status='completed').count()
    
    # SLA tracking (30-day GDPR requirement)
    overdue = GDPRRequest.objects.filter(
        status='pending',
        request_received_at__lte=today - timedelta(days=30)
    ).count()
    
    # Completion time
    completed_reqs = GDPRRequest.objects.filter(
        status='completed',
        completed_at__isnull=False
    )
    if completed_reqs.exists():
        avg_completion_time = sum(
            (r.completed_at - r.request_received_at).total_seconds()
            for r in completed_reqs
        ) / len(completed_reqs) / 86400  # Convert to days
    else:
        avg_completion_time = 0
    
    return {
        'total_requests': total_requests,
        'pending': pending,
        'completed': completed,
        'overdue': overdue,
        'avg_completion_days': round(avg_completion_time, 1),
        'sla_compliance': round(
            ((total_requests - overdue) / total_requests * 100)
            if total_requests > 0 else 100
        ),
    }
```

**Effort:** 8 hours

---

## 4. Database Schema Changes

```sql
-- New tables needed

CREATE TABLE core_useractivity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    activity_type VARCHAR(30),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, activity_type, created_at)
);

CREATE TABLE core_gdprrequest (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    request_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    reason VARCHAR(500),
    request_file VARCHAR(255),
    request_received_at TIMESTAMP DEFAULT NOW(),
    processing_started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

CREATE TABLE core_userconversionfunnel (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id),
    stage VARCHAR(30),
    reached_at TIMESTAMP DEFAULT NOW(),
    conversion_complete BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, stage)
);

-- Indexes for performance
CREATE INDEX idx_useractivity_user_date 
    ON core_useractivity(user_id, created_at);
CREATE INDEX idx_gdprrequest_status_date 
    ON core_gdprrequest(status, request_received_at);
CREATE INDEX idx_conversion_funnel_user 
    ON core_userconversionfunnel(user_id);
```

---

## 5. API Endpoints (New)

### Product Analytics API

**GET /api/analytics/v1/dashboard** (Admin)
```json
Response:
{
  "period": "30d",
  "metrics": {
    "engagement": {
      "dau": 150,
      "wau": 450,
      "mau": 1200,
      "active": 450,
      "at_risk": 120,
      "churned": 630
    },
    "revenue": {
      "active_subscriptions": 250,
      "estimated_mrr": 2500,
      "paying_users": 300,
      "free_users": 900,
      "arpu": 8.33
    },
    "conversion": {
      "total": 100,
      "converted": 15,
      "rate": 15,
      "funnel": [
        {"stage": "signup", "count": 100},
        {"stage": "first_journal", "count": 70},
        {"stage": "trial_day_7", "count": 45},
        {"stage": "payment_success", "count": 15}
      ]
    },
    "retention": {
      "day_1": 65,
      "day_7": 48,
      "day_30": 32,
      "cohorts": [...]
    },
    "churn": {
      "rate": 5.2,
      "at_risk": 45,
      "reason_breakdown": {...}
    },
    "emotions": {
      "top": [
        {"emotion": "hopeful", "count": 234},
        {"emotion": "peaceful", "count": 198}
      ],
      "trend": [...]
    },
    "gdpr": {
      "pending": 3,
      "completed": 47,
      "overdue": 0,
      "avg_completion_days": 5
    }
  }
}
```

**GET /api/analytics/v1/cohort/{cohort_date}** (Admin)
- Returns retention curve for specific cohort

**GET /api/analytics/v1/emotions/trend** (Admin)
- Returns emotion distribution over time

**GET /api/analytics/v1/programs/progress** (Admin)
- Returns program completion metrics

---

## 6. Frontend Dashboard Layout

### Admin Analytics Page

```
┌─────────────────────────────────────────────────────┐
│ Analytics Dashboard          Period: [7d] [30d] [90d] │
└─────────────────────────────────────────────────────┘

┌──────────┬──────────┬──────────┬──────────┐
│   DAU    │   WAU    │   MAU    │  Churn   │
│   150    │   450    │  1200    │  5.2% 🔴 │
└──────────┴──────────┴──────────┴──────────┘

┌───────────────────────────────┬──────────────────────┐
│                               │                      │
│  Engagement Tiers             │  Revenue             │
│  Super Active:  150 (12%)     │  Active Subs:  250   │
│  Active:       300 (25%)      │  MRR Est: $2,500     │
│  At Risk:      120 (10%)      │  ARPU: $8.33         │
│  Churned:      630 (53%)      │  Paying Ratio: 25%   │
│                               │                      │
└───────────────────────────────┴──────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Trial → Premium Conversion Funnel                    │
│ [Funnel chart with stages and drop-off]             │
│ Overall Rate: 15% (target: 25%)                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Retention Cohort (by signup week)                    │
│ Week      Day 1  Day 7  Day 14  Day 30  Day 60     │
│ Jan  1      65%    48%    36%     24%     12%      │
│ Jan  8      68%    50%    38%     26%     14%      │
│ Jan 15      70%    52%    40%     28%     15%      │
└─────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────┐
│  Emotions Trend  │  Program Progress                │
│  [Pie chart]     │  - Meditation: 45% complete     │
│  Hopeful: 40%    │  - Journaling: 62% complete     │
│  Peaceful: 35%   │  - Gratitude: 28% complete      │
│  Anxious: 15%    │  - Breathing: 71% complete      │
│  Sad: 10%        │                                  │
└──────────────────┴──────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ GDPR Compliance       🟢 SLA Compliant (100%)         │
│ Pending: 3 (0 Overdue)                               │
│ Completed: 47 (Avg: 5 days)                          │
└──────────────────────────────────────────────────────┘
```

---

## 7. Success Metrics

After implementation:

| Metric | Current | Target After |
|--------|---------|--------------|
| Dashboards available | 1 (admin) | 4+ (engagement, revenue, compliance, programs) |
| Metrics tracked | 8 | 50+ |
| Engagement visibility | ⚠️ Basic | ✅ Full DAU/WAU/MAU |
| Cohort analysis | ❌ | ✅ 10+ retention curves |
| Conversion funnel | ⚠️ Overall only | ✅ Trial-specific funnel |
| Revenue visibility | ❌ | ✅ MRR, ARPU, LTV |
| Emotion analytics | ❌ | ✅ Dashboard + trends |
| GDPR compliance | ❌ | ✅ Full audit trail |
| Data-driven decisions | 0% | 100% (enabled by dashboards) |

---

## 8. Implementation Priority

| Phase | Duration | Impact | Effort |
|-------|----------|--------|--------|
| Phase 1: Extend dashboard | 2 weeks | Add revenue, emotions, engagement | 30h |
| Phase 2: Analytics models | 3 weeks | Create retention, funnel, GDPR models | 40h |
| Phase 3: Public dashboards | 3 weeks | Frontend pages + API endpoints | 40h |
| Phase 4: GDPR compliance | 2 weeks | Request handling + audit trail | 20h |

**Total:** ~130 hours (1 month, 1 developer)

**Minimum MVP (Week 1):**
- Extend existing dashboard with engagement + emotions (30h)
- Add UserActivity model (12h)
- Deploy (6h)
- **Enables:** DAU/WAU/MAU, emotion trends, engagement tiers

---

## 9. Dependencies

- **Step 7 (Programs):** Must have UserProgramEnrollment model for progress tracking
- **Step 8 (Support AI):** Ticketing system can integrate with analytics
- **Step 9 (DevOps):** Backup GDPR data exports in S3

---

## 10. Files to Create/Modify

**Backend:**
- [ ] `backend/core/models.py` - Add UserActivity, GDPRRequest, UserConversionFunnel
- [ ] `backend/core/admin_dashboard.py` - Add new metric functions
- [ ] `backend/core/views.py` - Add AnalyticsDashboardView, GDPRRequestView
- [ ] `backend/core/admin.py` - Add admin pages for new models
- [ ] `backend/core/serializers.py` - Add analytics serializers
- [ ] `backend/core/migrations/` - Migration for new tables
- [ ] `backend/analytics/` - New app for analytics queries (optional)

**Frontend:**
- [ ] `frontend/pages/admin/analytics.vue` - Main dashboard page
- [ ] `frontend/components/analytics/` - Dashboard card components
- [ ] `frontend/composables/useAnalytics.ts` - API integration

**Tests:**
- [ ] `backend/core/tests/test_analytics.py` - Analytics calculation tests
- [ ] `frontend/tests/components/analytics/` - Component tests

---

## Next Steps

1. ✅ Audit complete
2. ❓ Approve Phase 1 (extend dashboard) - RECOMMENDED FIRST
3. ❓ Approve Phase 2-4 (full implementation)
4. ❓ Start implementation

---
