# Step 7: Guided Programs System Audit
**Status:** In Progress  
**Date:** 2026-03-11  
**Auditor:** Copilot  

---

## Executive Summary

The Guided Programs system is **incomplete and missing critical functionality**:

- ✅ **Data Models:** GuidedProgram and GuidedProgramDay exist (basic structure)
- ✅ **Basic API:** List programs and view day content
- ❌ **Progress Tracking:** MISSING - no user enrollment or day completion tracking
- ❌ **Navigation:** Users can only view day 1, no way to navigate between days
- ❌ **Completion Tracking:** No way to mark days/programs as complete
- ❌ **Admin Interface:** Limited - only can CRUD programs, no progress visibility
- ❌ **Frontend UX:** Only shows day 1, no day-by-day navigation, no progress bar

**Impact:** Programs are **read-only content display**, not interactive guided learning experiences.

---

## 1. Current Implementation

### 1.1 Backend Models

**GuidedProgram**
```python
class GuidedProgram(models.Model):
    title = CharField(max_length=200)
    description = TextField(blank=True)
    language = CharField(max_length=2)  # ro/en/de/es/it/pl
    active = BooleanField(default=True)
    is_premium = BooleanField(default=False)
```

**Issues:**
- ❌ No owner/creator field (who created this program?)
- ❌ No category field (type of program: wellness, productivity, etc.)
- ❌ No duration field (how many days?)
- ❌ No metadata (difficulty, tags, target audience)
- ✅ Tier control works (is_premium)

**GuidedProgramDay**
```python
class GuidedProgramDay(models.Model):
    program = ForeignKey(GuidedProgram)
    day_number = PositiveIntegerField()
    title = CharField(max_length=200)
    content = TextField()
    question = TextField(blank=True)  # Reflection question
    ai_prompt = TextField(blank=True)  # Unused?
```

**Issues:**
- ❌ No optional fields (some days might not have questions)
- ❌ `ai_prompt` field exists but never used in API/views
- ❌ No multimedia support (images, videos)
- ❌ No dependencies (prerequisites before viewing day)
- ✅ Structure is logical

### Status: ⚠️ Basic but sufficient for data storage

---

### 1.2 Backend APIs

**Endpoints:**

1. **GET /programs**
   ```
   Auth: IsAuthenticated
   Permission: has_paid_access()
   Returns: List of active programs in user's language
   
   Response:
   [
     {
       "id": 1,
       "title": "7-Day Clarity Program",
       "description": "...",
       "language": "en",
       "is_premium": false,
       "active": true
     }
   ]
   ```
   
   Issues:
   - ❌ Doesn't show current user's progress (which programs they started)
   - ❌ Doesn't show completion status
   - ❌ Doesn't show how many days in each program
   - Status: Bare minimum

2. **GET /programs/{program_id}/days/{day_number}**
   ```
   Auth: IsAuthenticated
   Permission: has_paid_access()
   
   Returns single day:
   {
     "id": 1,
     "program": 1,
     "day_number": 1,
     "title": "Day 1: Intro",
     "content": "...",
     "question": "...",
     "ai_prompt": "..."
   }
   ```
   
   Issues:
   - ❌ No way to know if user has already completed this day
   - ❌ No previous/next day links
   - ❌ No progress context (day X of Y)
   - Status: Read-only content delivery

**Missing Endpoints:**
- ❌ `GET /programs/{id}` - Get program with all days
- ❌ `GET /programs/{id}/progress` - Get user's progress on this program
- ❌ `POST /programs/{id}/enroll` - Start a program
- ❌ `POST /programs/{id}/days/{day}/complete` - Mark day complete
- ❌ `PUT /programs/{id}/days/{day}/reflection` - Save day's reflection answer

### Status: ❌ Minimal - only supports viewing content

---

### 1.3 Frontend Pages

**programs/index.vue**
- ✅ Displays list of programs
- ✅ Shows title, description, premium badge
- ✅ Links to program detail page
- ❌ Doesn't show progress on started programs
- ❌ Doesn't show which programs user has completed

**programs/[id].vue**
```vue
<!-- Only shows day 1, hardcoded: /programs/{id}/days/1 -->
<script setup>
const day = await fetchApi(`/programs/${id}/days/1`)
</script>
```

**Issues:**
- ❌ Always fetches day 1, ignores day parameter
- ❌ No navigation between days (prev/next buttons)
- ❌ No day selector (jump to day 5, etc.)
- ❌ No progress indicator
- ❌ No completion marking UI
- ❌ No reflection question input
- ❌ No completion celebration/certificate

### Status: ❌ Very limited UX - can only see day 1

---

### 1.4 Admin Interface

**GuidedProgramAdmin**
```python
list_display = ("title", "language", "is_premium", "active")
list_filter = ("language", "is_premium")
inlines = [GuidedProgramDayInline]
```

**Issues:**
- ✅ Can create programs and days
- ❌ Can't see how many users enrolled
- ❌ Can't see completion rates
- ❌ Can't see which programs are popular
- ❌ No enrollment statistics
- ❌ No user progress visibility

### Status: ⚠️ Basic admin, missing analytics

---

## 2. What's Missing

### Critical: User Progress Tracking

**Missing Model: UserProgramEnrollment** (or UserProgramProgress)
```python
class UserProgramEnrollment(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    program = ForeignKey(GuidedProgram, on_delete=models.CASCADE)
    enrolled_at = DateTimeField(auto_now_add=True)
    started_at = DateTimeField(null=True)  # First day viewed
    completed_at = DateTimeField(null=True)  # All days completed
    current_day = PositiveIntegerField(default=1)  # Progress tracking
    is_active = BooleanField(default=True)  # Paused/abandoned
    
    class Meta:
        unique_together = [("user", "program")]
```

**Purpose:** Track which users are enrolled in which programs

---

### Critical: Day Completion Tracking

**Missing Model: UserProgramDayCompletion**
```python
class UserProgramDayCompletion(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    day = ForeignKey(GuidedProgramDay, on_delete=models.CASCADE)
    reflection_answer = TextField(blank=True)  # User's reflection
    completed_at = DateTimeField(auto_now_add=True)
    time_spent_seconds = IntegerField(default=0)  # How long they spent
    ai_response = TextField(blank=True)  # AI feedback on reflection
    
    class Meta:
        unique_together = [("user", "day")]
    
    @property
    def days_after_started(self):
        """How many days after enrolling they completed this"""
        enrollment = UserProgramEnrollment.objects.get(
            user=self.user, 
            program=self.day.program
        )
        return (self.completed_at - enrollment.started_at).days
```

**Purpose:** Track which days each user completed, when, and their reflection answers

---

### High: Navigation & Context APIs

**Missing Endpoints:**
1. `GET /programs/{id}` - Full program details with all days
2. `GET /programs/{id}/progress` - User's enrollment + completion status
3. `POST /programs/{id}/enroll` - Start a program
4. `POST /programs/{id}/days/{day_number}/complete` - Mark day complete
5. `GET /programs/my-programs` - List user's enrolled programs with progress

---

### High: Frontend Navigation

**Missing UI:**
- [ ] Day-by-day navigation (prev/next buttons)
- [ ] Day selector/progress bar showing current position
- [ ] "Day X of Y" indicator
- [ ] Completion checkmarks for past days
- [ ] "Completed on [date]" for finished days
- [ ] Reflection input form on each day
- [ ] Completion celebration screen
- [ ] Ability to pause/resume programs

---

### Medium: AI Integration

**Unused Field:** `ai_prompt` in GuidedProgramDay

**Opportunity:** After user submits reflection, send to AI:
```
User submitted reflection: "..."
For program: "7-Day Clarity"
Prompt: "Provide encouraging feedback on this reflection while referencing their program theme"
Response: Store in UserProgramDayCompletion.ai_response
```

---

### Medium: Analytics & Admin Dashboard

**Missing:**
- [ ] Per-program enrollment count
- [ ] Per-program completion rate
- [ ] Most popular programs
- [ ] Average time per program
- [ ] User progress dashboard (admins can see who's on day 3, etc.)
- [ ] Dropout analysis (when do people stop?)

---

## 3. Recommended Implementation Plan

### Phase 1: Critical Infrastructure (1-2 weeks)

**1.1 Create Missing Models**
- [ ] `UserProgramEnrollment` - Track enrollments
- [ ] `UserProgramDayCompletion` - Track day completions & reflections

**1.2 Migrations**
- [ ] Create migrations for new models
- [ ] Add indexes for fast queries (user + program)

**1.3 Core APIs**
- [ ] `POST /programs/{id}/enroll` - Start program
- [ ] `GET /programs/{id}/progress` - Get enrollment + completion status
- [ ] `GET /programs/{id}/days/{day}` - Enhanced with completion info
- [ ] `POST /programs/{id}/days/{day}/complete` - Mark day done with reflection

**1.4 Frontend Updates**
- [ ] Modify `programs/[id].vue` to handle dynamic day navigation
- [ ] Add day selector component
- [ ] Add reflection input form
- [ ] Add day navigation buttons (prev/next)
- [ ] Add progress indicator/progress bar

**Effort:** ~60 hours (40 backend, 20 frontend)

---

### Phase 2: Enhanced Features (1 week)

**2.1 Completion Tracking**
- [ ] Automatic completion detection (when all days done)
- [ ] Completion certificate/badge
- [ ] Completion email notification

**2.2 AI Integration**
- [ ] Add AI feedback on reflections
- [ ] Store AI responses

**2.3 Admin Dashboard**
- [ ] Add enrollment stats to admin
- [ ] Add completion rate charts
- [ ] User progress table (who's on which day)

**Effort:** ~40 hours (25 backend, 15 frontend)

---

### Phase 3: Polish & Analytics (1 week)

**3.1 UX Improvements**
- [ ] Pause/resume functionality
- [ ] Filters on programs list (completed, in-progress, available)
- [ ] Program recommendations based on user interests

**3.2 Analytics**
- [ ] Track program engagement metrics
- [ ] Identify dropout points
- [ ] Calculate completion rate by day

**3.3 Notifications**
- [ ] Daily reminder to continue program
- [ ] "You've paused this program" notification
- [ ] Completion celebration email

**Effort:** ~30 hours (15 backend, 15 frontend)

---

## 4. Database Schema (Phase 1)

```sql
-- New table: User program enrollments
CREATE TABLE programs_userprogramenrollment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id),
    program_id INTEGER NOT NULL REFERENCES programs_guidedprogram(id),
    enrolled_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    current_day INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, program_id)
);

-- New table: Day completions with reflection answers
CREATE TABLE programs_userprogramdaycompletion (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id),
    day_id INTEGER NOT NULL REFERENCES programs_guidedprogramday(id),
    reflection_answer TEXT,
    ai_response TEXT,
    time_spent_seconds INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, day_id)
);

CREATE INDEX idx_enrollment_user ON programs_userprogramenrollment(user_id);
CREATE INDEX idx_enrollment_program ON programs_userprogramenrollment(program_id);
CREATE INDEX idx_completion_user ON programs_userprogramdaycompletion(user_id);
CREATE INDEX idx_completion_day ON programs_userprogramdaycompletion(day_id);
```

---

## 5. API Specification (Phase 1)

### Endpoint: POST /programs/{id}/enroll
```
Request:
{
  "program_id": 1
}

Response (201):
{
  "enrollment_id": 42,
  "program_id": 1,
  "enrolled_at": "2026-03-11T10:00:00Z",
  "started_at": "2026-03-11T10:00:00Z",
  "current_day": 1,
  "total_days": 7,
  "is_active": true
}

Error Responses:
- 404: Program not found
- 403: User lacks access (premium only or trial expired)
- 409: Already enrolled
```

---

### Endpoint: GET /programs/{id}/progress
```
Response (200):
{
  "program": {
    "id": 1,
    "title": "7-Day Clarity",
    "total_days": 7
  },
  "enrollment": {
    "is_enrolled": true,
    "enrolled_at": "2026-03-11T10:00:00Z",
    "is_completed": false,
    "current_day": 3
  },
  "completions": [
    {
      "day_number": 1,
      "completed_at": "2026-03-11T10:30:00Z",
      "reflection_answer": "Today I learned...",
      "ai_response": "Great insight..."
    },
    {
      "day_number": 2,
      "completed_at": "2026-03-12T10:30:00Z",
      "reflection_answer": "...",
      "ai_response": "..."
    }
  ],
  "stats": {
    "completion_percentage": 28,  // 2/7
    "estimated_days_until_complete": 5
  }
}

Error: 404 if not enrolled
```

---

### Endpoint: POST /programs/{id}/days/{day}/complete
```
Request:
{
  "reflection_answer": "Today I realized that..."
}

Response (200):
{
  "day": {
    "day_number": 3,
    "title": "Day 3: Reflection"
  },
  "completion": {
    "completed_at": "2026-03-13T10:30:00Z",
    "reflection_answer": "Today I realized...",
    "ai_response": "That's excellent progress..."
  },
  "progress": {
    "current_day": 4,
    "completion_percentage": 43,
    "days_remaining": 4
  }
}

Error: 
- 404: Day not found
- 403: User not enrolled
- 409: Already completed today (rate limit)
```

---

### Endpoint: GET /programs/my-programs
```
Response (200):
[
  {
    "id": 1,
    "title": "7-Day Clarity",
    "status": "in_progress",
    "enrolled_at": "2026-03-11T10:00:00Z",
    "started_at": "2026-03-11T10:00:00Z",
    "current_day": 3,
    "total_days": 7,
    "completion_percentage": 28,
    "last_completed_at": "2026-03-13T10:30:00Z"
  },
  {
    "id": 2,
    "title": "21-Day Habit Builder",
    "status": "not_started",
    "enrolled_at": "2026-03-10T09:00:00Z",
    "started_at": null,
    "current_day": 0,
    "total_days": 21,
    "completion_percentage": 0
  },
  {
    "id": 3,
    "title": "Emotional Clarity",
    "status": "completed",
    "enrolled_at": "2026-01-01T09:00:00Z",
    "started_at": "2026-01-01T09:00:00Z",
    "completed_at": "2026-01-21T18:00:00Z",
    "current_day": 20,
    "total_days": 20,
    "completion_percentage": 100
  }
]
```

---

## 6. Frontend Component Updates

### programs/[id].vue Changes

**Current:** Only shows day 1  
**New:** Shows dynamic day with navigation

```vue
<template>
  <div class="max-w-2xl mx-auto">
    <NuxtLink :to="localePath('/programs')">Back</NuxtLink>
    
    <!-- Progress bar -->
    <div class="mt-4 sticky top-0 bg-white p-4 border-b">
      <div class="flex items-center justify-between mb-2">
        <h2 class="font-bold">{{ program.title }}</h2>
        <span class="text-sm text-stone-600">{{ currentDay }} / {{ totalDays }}</span>
      </div>
      <ProgressBar :value="(currentDay / totalDays) * 100" />
    </div>
    
    <!-- Day content -->
    <div v-if="day" class="py-6 space-y-4">
      <h1 class="text-3xl font-bold">{{ day.title }}</h1>
      <p class="text-stone-600 whitespace-pre-wrap">{{ day.content }}</p>
      
      <!-- Reflection form -->
      <form v-if="!isCompleted" @submit.prevent="submitReflection" class="border-t pt-6 space-y-4">
        <label>
          <span class="font-medium">{{ day.question }}</span>
          <textarea
            v-model="reflectionText"
            rows="5"
            class="w-full mt-2 border rounded-lg p-3"
          />
        </label>
        <button class="btn btn-primary">Mark Day Complete</button>
      </form>
      
      <!-- Already completed -->
      <div v-else class="bg-green-50 border border-green-200 p-4 rounded-lg">
        ✓ Completed on {{ formattedDate }}
        <p class="text-sm mt-2">Your response: "{{ completion.reflection_answer }}"</p>
        <p v-if="completion.ai_response" class="text-sm mt-2">
          AI feedback: "{{ completion.ai_response }}"
        </p>
      </div>
    </div>
    
    <!-- Navigation -->
    <div class="flex justify-between mt-8 border-t pt-4">
      <button
        v-if="currentDay > 1"
        @click="goToDay(currentDay - 1)"
        class="btn btn-secondary"
      >
        ← Previous Day
      </button>
      <button
        v-if="currentDay < totalDays"
        @click="goToDay(currentDay + 1)"
        class="btn btn-secondary"
      >
        Next Day →
      </button>
      <div v-else class="text-center">
        <p class="font-bold text-green-600">🎉 Program Complete!</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'subscription'] })

const route = useRoute()
const router = useRouter()
const { fetchApi } = useApi()
const { locale } = useI18n()
const localePath = useLocalePath()

const program = ref(null)
const day = ref(null)
const currentDay = ref(1)
const totalDays = ref(0)
const reflectionText = ref('')
const isCompleted = ref(false)
const completion = ref(null)
const loading = ref(true)

const formattedDate = computed(() => {
  if (!completion.value?.completed_at) return ''
  return new Date(completion.value.completed_at).toLocaleDateString()
})

onMounted(async () => {
  const programId = route.params.id
  
  // Get program info
  const progress = await fetchApi(`/programs/${programId}/progress`)
  currentDay.value = progress.enrollment.current_day
  totalDays.value = progress.program.total_days
  program.value = progress.program
  
  // Get day content
  await loadDay(currentDay.value)
  
  loading.value = false
}

async function loadDay(dayNum) {
  const day = await fetchApi(`/programs/${route.params.id}/days/${dayNum}`)
  // Check if user already completed
  const progress = await fetchApi(`/programs/${route.params.id}/progress`)
  const completion = progress.completions.find(c => c.day_number === dayNum)
  
  isCompleted.value = !!completion
  isCompleted.value && (completion.value = completion)
}

async function submitReflection() {
  const res = await fetchApi(`/programs/${route.params.id}/days/${currentDay.value}/complete`, {
    method: 'POST',
    body: { reflection_answer: reflectionText.value }
  })
  
  isCompleted.value = true
  completion.value = res.completion
  if (res.progress.current_day > currentDay.value) {
    currentDay.value = res.progress.current_day
  }
}

function goToDay(dayNum) {
  currentDay.value = dayNum
  loadDay(dayNum)
}
</script>
```

---

## 7. Access Control

### Who can enroll?
- ✅ Users with active trial
- ✅ Users with paid subscription (BASIC/PREMIUM/VIP)
- ❌ Free tier users (no access)
- ⚠️ Add: Different programs for different tiers (is_premium flagging)

### Who can complete?
- ✅ Enrolled users only
- ✅ Rate-limit: Max 1 completion per day per user
- ⚠️ Add: Optional daily streak tracking

---

## 8. Implementation Files

### Backend Files to Create/Modify:
- [ ] `backend/programs/models.py` - Add `UserProgramEnrollment`, `UserProgramDayCompletion`
- [ ] `backend/programs/serializers.py` - Add serializers for new models
- [ ] `backend/programs/views.py` - Add new endpoints
- [ ] `backend/programs/admin.py` - Add admin for new models
- [ ] `backend/programs/migrations/` - Create migrations

### Frontend Files to Modify:
- [ ] `frontend/pages/programs/[id].vue` - Complete rewrite
- [ ] `frontend/components/ProgramCard.vue` - Show progress status
- [ ] `frontend/pages/programs/index.vue` - Show program status (in-progress, completed, etc.)

### Tests to Create:
- [ ] `backend/programs/tests/test_enrollment.py` - Enrollment logic
- [ ] `backend/programs/tests/test_completion.py` - Day completion tracking
- [ ] `backend/programs/tests/test_access_control.py` - Tier-based access

---

## 9. Success Metrics

After implementation, measure:

### User Engagement
- [ ] Enrollment rate (% of users who start a program)
- [ ] Completion rate (% who finish all days)
- [ ] Average time per program
- [ ] Dropout point (which day do they stop?)

### Feature Health
- [ ] Programs with < 20% completion rate should be reviewed
- [ ] Programs with > 70% completion rate are good
- [ ] Average engagement: users should complete 1-2 programs/quarter

### Business Impact
- [ ] Programs can drive retention (users who complete stay longer)
- [ ] Programs can increase ARPU (users complete → upgrade to PREMIUM)
- [ ] Programs can reduce churn (active users engage more)

---

## 10. Risk Assessment

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Users abandon halfway | HIGH | MEDIUM | Daily reminders, motivational emails |
| Slow program queries | LOW | HIGH | Proper indexing, caching |
| Data spam (many completions) | LOW | LOW | Rate limiting (1/day per user/day) |
| AI feedback errors | MEDIUM | MEDIUM | Review before showing user critical feedback |

---

## Next Steps

1. ✅ Audit complete
2. ❓ Approve Phase 1 implementation plan
3. ❓ Start with model creation + migrations
4. ❓ Implement backend APIs
5. ❓ Update frontend navigation
6. ❓ Test end-to-end flow

---
