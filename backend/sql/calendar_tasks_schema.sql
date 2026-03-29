-- Calendar & Task module schema for Doisense (PostgreSQL)

CREATE TABLE IF NOT EXISTS calendar_plan (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(16) NOT NULL UNIQUE CHECK (code IN ('basic', 'premium', 'vip')),
  name VARCHAR(64) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  capabilities JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS calendar_user_plan (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
  plan_id BIGINT NOT NULL REFERENCES calendar_plan(id) ON DELETE RESTRICT,
  source VARCHAR(16) NOT NULL DEFAULT 'system' CHECK (source IN ('system', 'admin', 'payment')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS calendar_up_user_active_idx ON calendar_user_plan(user_id, is_active);
CREATE INDEX IF NOT EXISTS calendar_up_exp_idx ON calendar_user_plan(expires_at);

CREATE TABLE IF NOT EXISTS calendar_task (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
  title VARCHAR(180) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  duration_minutes INTEGER NOT NULL DEFAULT 15 CHECK (duration_minutes BETWEEN 5 AND 600),
  frequency VARCHAR(16) NOT NULL DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly', 'monthly', 'custom')),
  weekdays JSONB NOT NULL DEFAULT '[]'::jsonb,
  month_days JSONB NOT NULL DEFAULT '[]'::jsonb,
  start_time TIME NULL,
  reminder_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  reminder_minutes_before INTEGER NOT NULL DEFAULT 10 CHECK (reminder_minutes_before BETWEEN 0 AND 1440),
  advanced_options JSONB NOT NULL DEFAULT '{}'::jsonb,
  ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
  ai_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  starts_on DATE NOT NULL,
  ends_on DATE NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (ends_on IS NULL OR ends_on >= starts_on)
);

CREATE INDEX IF NOT EXISTS calendar_task_user_active_idx ON calendar_task(user_id, is_active);
CREATE INDEX IF NOT EXISTS calendar_task_user_start_idx ON calendar_task(user_id, starts_on);
CREATE INDEX IF NOT EXISTS calendar_task_user_created_idx ON calendar_task(user_id, created_at);

CREATE TABLE IF NOT EXISTS calendar_task_progress (
  id BIGSERIAL PRIMARY KEY,
  task_id BIGINT NOT NULL REFERENCES calendar_task(id) ON DELETE CASCADE,
  user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
  progress_date DATE NOT NULL,
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMPTZ NULL,
  note VARCHAR(280) NOT NULL DEFAULT '',
  mood_score SMALLINT NULL,
  energy_score SMALLINT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT calendar_tp_task_day_uq UNIQUE (task_id, progress_date)
);

CREATE INDEX IF NOT EXISTS calendar_tp_user_day_idx ON calendar_task_progress(user_id, progress_date);
CREATE INDEX IF NOT EXISTS calendar_tp_task_day_idx ON calendar_task_progress(task_id, progress_date);

CREATE TABLE IF NOT EXISTS calendar_task_stat (
  id BIGSERIAL PRIMARY KEY,
  task_id BIGINT NOT NULL UNIQUE REFERENCES calendar_task(id) ON DELETE CASCADE,
  completed_days INTEGER NOT NULL DEFAULT 0,
  total_days INTEGER NOT NULL DEFAULT 0,
  current_streak INTEGER NOT NULL DEFAULT 0,
  best_streak INTEGER NOT NULL DEFAULT 0,
  completion_rate NUMERIC(6,2) NOT NULL DEFAULT 0,
  last_completed_at TIMESTAMPTZ NULL,
  last_calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS calendar_ts_rate_idx ON calendar_task_stat(completion_rate);

INSERT INTO calendar_plan (code, name, description, capabilities)
VALUES
  ('basic', 'BASIC Start', 'manual tasks + simple progress', '{"task_create":true,"task_check":true,"task_active_view":true,"simple_progress":true,"chat_month_calendar":true,"advanced_stats":false,"task_history":false,"profile_monthly_view":false,"advanced_task_options":false,"ai_habit_suggestions":false,"ai_routine_builder":false,"ai_daily_checkin":false,"ai_progress_insights":false,"ai_habit_optimization":false}'::jsonb),
  ('premium', 'PREMIUM Flow', 'basic + advanced statistics + history + monthly view', '{"task_create":true,"task_check":true,"task_active_view":true,"simple_progress":true,"chat_month_calendar":true,"advanced_stats":true,"task_history":true,"profile_monthly_view":true,"advanced_task_options":true,"ai_habit_suggestions":false,"ai_routine_builder":false,"ai_daily_checkin":false,"ai_progress_insights":false,"ai_habit_optimization":false}'::jsonb),
  ('vip', 'VIP Executive', 'premium + AI suggestions, routines, check-ins and insights', '{"task_create":true,"task_check":true,"task_active_view":true,"simple_progress":true,"chat_month_calendar":true,"advanced_stats":true,"task_history":true,"profile_monthly_view":true,"advanced_task_options":true,"ai_habit_suggestions":true,"ai_routine_builder":true,"ai_daily_checkin":true,"ai_progress_insights":true,"ai_habit_optimization":true}'::jsonb)
ON CONFLICT (code) DO NOTHING;
