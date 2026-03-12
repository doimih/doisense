# Analytics Event Schema (v1)

Acest document definește schema minimă pentru evenimentele platformei.

Platformă recomandată:
- PostHog (integrare opțională prin POSTHOG_API_KEY)

Persistență locală:
- core_analyticsevent (pentru audit intern + fallback)

## Events

- user_registered
  - auth_method
- user_activated
  - auth_method
- onboarding_started
  - tier_variant
- onboarding_step_completed
  - step_key
  - step_index
  - tier_variant
- onboarding_profile_saved
  - has_journal
  - tier_variant
- onboarding_completed
  - tier_variant
- onboarding_restarted
  - entrypoint
- chat_message_sent
  - module
- journal_entry_created
  - question_id
- program_day_completed
  - program_id
  - day_number
- program_completed
  - program_id
  - day_number
- program_paused
  - program_id
  - day_number
- program_resumed
  - program_id
  - day_number
- program_reflection_submitted
  - program_id
  - day_number
- program_dropout_detected
  - program_id
  - day_number
- checkout_initiated
  - plan_tier
- subscription_change_requested
  - plan_tier
- subscription_cancel_requested
  - plan_tier
- subscription_refunded
  - plan_tier
- support_ticket_created
- feature_access_checked
  - feature_key
  - granted

## Coverage Map

- onboarding: user_registered, user_activated
- onboarding flow: onboarding_started, onboarding_step_completed, onboarding_profile_saved, onboarding_completed, onboarding_restarted
- chat: chat_message_sent
- journal: journal_entry_created
- programs: program_day_completed, program_completed, program_paused, program_resumed, program_reflection_submitted, program_dropout_detected
- payments: checkout_initiated, subscription_change_requested, subscription_cancel_requested, subscription_refunded
- support: support_ticket_created
- governance: feature_access_checked
