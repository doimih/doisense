# Social Media AI System

## 1. Overview

The Social Media AI System is an extension inside the AI Brain domain (`ai_core`) for creating, storing, reviewing, and publishing wellness-focused social content.

It provides:
- Data models for post content and platform credentials
- A generation service that enforces wellness constraints
- Publishing services for Instagram, TikTok, and LinkedIn
- Admin UX for generation, content lifecycle management, and platform configuration
- Full auditability through per-post publish logs

Core design goals:
- Keep existing AI/orchestrator logic untouched
- Add functionality as isolated, additive modules
- Enforce wellness-only content and platform-aware closing lines
- Maintain safe defaults and explicit failure logging

---

## 2. Module-by-Module Documentation

### 2.1 `SocialMediaPost` (`ai_core.models`)

**Purpose**
Stores generated social content and publication state.

**Model fields**
- `platform`: target platform enum
  - `instagram`
  - `tiktok`
  - `linkedin`
- `title`: post title
- `body`: main content body
- `hashtags`: serialized hashtag string
- `image_url`: image/media URL (placeholder or real media URL)
- `wellness_topic`: normalized wellness topic
- `status`: lifecycle state
  - `draft` (default)
  - `posted`
- `created_at`: creation timestamp
- `posted_at`: successful publish timestamp (nullable)
- `publish_log`: append-only textual operational log

**Operational notes**
- All generated posts are saved as `draft` first.
- Publishing modules change status to `posted` only on successful API call.
- `publish_log` is used for operational traceability and troubleshooting.

---

### 2.2 `SocialMediaSettings` (`ai_core.models`)

**Purpose**
Singleton settings store for social platform API credentials and IDs.

**Instagram fields**
- `instagram_app_id`
- `instagram_app_secret`
- `instagram_access_token`
- `instagram_refresh_token`
- `instagram_business_account_id`

**TikTok fields**
- `tiktok_app_id`
- `tiktok_app_secret`
- `tiktok_access_token`
- `tiktok_refresh_token`

**LinkedIn fields**
- `linkedin_client_id`
- `linkedin_client_secret`
- `linkedin_access_token`
- `linkedin_refresh_token`
- `linkedin_organization_id`

**Singleton behavior**
- `save()` enforces `pk=1`
- `load()` returns existing row or creates it automatically

**Admin behavior**
- Add is disabled if record already exists
- Delete is disabled
- Changelist redirects to singleton change form

---

### 2.3 `social_media.py`

**Purpose**
Contains post generation and persistence helpers.

#### `generate_social_post(topic, platform)`
Builds structured social content with required constraints:
- Wellness-topic normalization
- Platform-adapted writing tone
- Platform-specific closing line
- Hashtag generation
- Rule linkage via AI Brain rules prompt lookup

**Key behavior details**
- Non-wellness topics are auto-normalized to wellness context via `_normalize_wellness_topic`.
- Tone map (`PLATFORM_TONES`):
  - Instagram: inspirational, concise, visual-first
  - TikTok: energetic, short, trend-aware
  - LinkedIn: professional, practical, reflective
- Closing line is always appended and platform-specific.

#### `generate_social_image(prompt)`
Returns a placeholder image URL based on a sanitized prompt.

Current implementation uses `dummyimage.com` as a placeholder generator endpoint.

#### `save_generated_post(data)`
Persists a generated post into `SocialMediaPost`.

Typical use:
- Called automatically by Generator admin after generation
- Can also be used to save edited draft data

---

### 2.4 `publish_instagram.py`

**Purpose**
Publishes a `SocialMediaPost` to Instagram Graph API.

**Function**
`publish_to_instagram(post) -> (ok: bool, message: str)`

**Flow**
1. Load singleton settings via `SocialMediaSettings.load()`
2. Validate required data:
   - `instagram_access_token`
   - `instagram_business_account_id`
3. Validate token basic sanity (length check)
4. Build API request:
   - Endpoint: `https://graph.facebook.com/v20.0/{business_account_id}/media`
   - Payload includes caption, image URL, access token
5. On success:
   - Append publish log
   - Set `status=posted`
   - Set `posted_at`
6. On failure:
   - Capture HTTP/general exception details
   - Append publish log
   - Keep post in draft state

---

### 2.5 `publish_tiktok.py`

**Purpose**
Publishes a `SocialMediaPost` to TikTok API.

**Function**
`publish_to_tiktok(post) -> (ok: bool, message: str)`

**Flow**
1. Load settings singleton
2. Validate required data:
   - `tiktok_app_id`
   - `tiktok_access_token`
3. Validate token basic sanity
4. Build API request:
   - Endpoint: `https://open.tiktokapis.com/v2/post/publish/content/init/`
   - Authorization: Bearer token
   - Payload includes post info and source URL
5. On success: set `posted` state and update logs
6. On failure: retain draft state and append error log

---

### 2.6 `publish_linkedin.py`

**Purpose**
Publishes a `SocialMediaPost` to LinkedIn UGC API.

**Function**
`publish_to_linkedin(post) -> (ok: bool, message: str)`

**Flow**
1. Load settings singleton
2. Validate required data:
   - `linkedin_access_token`
   - `linkedin_organization_id`
3. Validate token basic sanity
4. Build API request:
   - Endpoint: `https://api.linkedin.com/v2/ugcPosts`
   - Headers include bearer token and Rest.li protocol version
   - Payload uses organization URN author and text commentary
5. On success: set `posted`, set timestamp, append success log
6. On failure: append failure details, keep draft status

---

### 2.7 Social Media Generator Admin

**Entry point**
- URL: `/admin/ai_core/social-generator/`
- Implemented as custom admin view in `ai_core.admin`

**Features**
- Select platform
- Input content topic
- Generate content and image preview
- Auto-save generated draft to DB
- Edit and save generated values (title/body/hashtags/image/topic)

**Security**
- Requires `ai_core.add_socialmediapost`

**Template**
- `backend/templates/admin/ai_core/social_generator.html`

---

### 2.8 Social Media Content Admin

**Model admin**
`SocialMediaPostAdmin`

**List behavior**
- `list_display`: platform, title, wellness_topic, status, created_at
- `list_filter`: platform, wellness_topic, status
- `search_fields`: title, body

**Actions**
- Publish to Instagram
- Publish to TikTok
- Publish to LinkedIn

**Action safety**
- If selected action platform does not match post platform, item is skipped and skip reason is logged in `publish_log`.
- Success/failure counts are surfaced through admin messages.

---

### 2.9 Social Media API Settings Admin

**Model admin**
`SocialMediaSettingsAdmin`

**Location in sidebar**
- `Platform Settings -> Social Media API Settings`

**UI structure**
Credentials grouped by platform:
- Instagram section
- TikTok section
- LinkedIn section

**Singleton enforcement**
- No delete allowed
- Add disabled after first record
- Changelist redirects directly to singleton edit form

---

## 3. Workflow

The primary lifecycle is:

`generate -> save -> list -> publish -> log`

Detailed flow:
1. Admin opens Social Media Generator.
2. Admin enters topic and platform.
3. System generates wellness-safe content and platform-specific closing line.
4. System auto-saves a draft post in `SocialMediaPost`.
5. Admin reviews/edits in Generator preview or in Social Media Content list.
6. Admin runs publish action for the target platform.
7. Publisher module attempts API POST.
8. On success: post status becomes `posted`, `posted_at` set, success logged.
9. On failure: status remains `draft`, failure details appended to `publish_log`.

---

## 4. Configuration

### 4.1 How to set API keys

1. Open Django Admin.
2. Navigate to:
   - `Platform Settings -> Social Media API Settings`
3. Fill required credentials per platform.
4. Save.

### 4.2 Required fields per platform

#### Instagram (required for publish)
- `instagram_access_token`
- `instagram_business_account_id`

#### TikTok (required for publish)
- `tiktok_app_id`
- `tiktok_access_token`

#### LinkedIn (required for publish)
- `linkedin_access_token`
- `linkedin_organization_id`

### 4.3 Optional fields

These are stored for future token lifecycle/extended flows, but not strictly required by current publish checks:
- App/Client IDs and secrets not listed above as required
- Refresh tokens

### 4.4 Rules prompt dependency

A rules prompt seed is created by migration as:
- Name: `social_media_global_wellness_rules`
- Type: `rules`

Generation logic attempts to load a social-media rules prompt from AI Brain rules. If not found, it falls back to an internal default string.

---

## 5. Operations Guide

### 5.1 Generating posts

1. Go to `AI Brain -> Social Media Generator`.
2. Choose platform (`instagram`, `tiktok`, or `linkedin`).
3. Enter topic.
4. Click **Generate + Auto Save Draft**.

Result:
- Draft created in DB automatically
- Preview rendered for immediate review/edit

### 5.2 Reviewing content

Two review paths:
- In generator preview form (immediate post-generation)
- In `AI Brain -> Social Media Content` changelist

Recommended review checklist:
- Title clarity and platform fit
- Body tone and wellness alignment
- Closing line mentions correct platform
- Hashtags relevant to topic
- Media URL valid for intended platform

### 5.3 Publishing

1. Open `AI Brain -> Social Media Content`.
2. Filter by platform and status (`draft`).
3. Select one or more rows.
4. Run matching publish action:
   - Instagram posts -> Publish to Instagram
   - TikTok posts -> Publish to TikTok
   - LinkedIn posts -> Publish to LinkedIn

Notes:
- Cross-platform action mismatches are skipped and logged.
- On success, status transitions to `posted`.

### 5.4 Checking logs

Use `publish_log` in the post detail page to inspect:
- Validation failures (missing settings/token too short)
- API response summaries
- HTTP error details
- Skip reasons for platform mismatch

`publish_log` is the primary operational audit trail for publishing outcomes.

---

## 6. File Map

### Backend modules
- `backend/ai_core/models.py`
- `backend/ai_core/social_media.py`
- `backend/ai_core/publish_instagram.py`
- `backend/ai_core/publish_tiktok.py`
- `backend/ai_core/publish_linkedin.py`
- `backend/ai_core/admin.py`

### Migration
- `backend/ai_core/migrations/0002_social_media_models_and_rules_prompt.py`

### Admin template
- `backend/templates/admin/ai_core/social_generator.html`

### Sidebar integration
- `backend/config/settings.py`

---

## 7. Operational Caveats and Recommendations

- Token validation is currently minimal (presence + length check). For production hardening, add token introspection/refresh flows where available.
- `generate_social_image()` currently returns a placeholder URL provider. Replace with real media generation/storage pipeline before production media campaigns.
- Publishing currently assumes one-shot publish. If queueing, retries, or backoff are needed, integrate async task orchestration.
- Consider enforcing stricter hashtag/length policies per platform before publish.

---

## 8. Quick Runbook

1. Apply migrations: `python manage.py migrate`
2. Configure credentials in admin singleton
3. Generate draft content from Generator page
4. Review and edit content
5. Publish via platform-specific admin action
6. Verify status and inspect `publish_log`
