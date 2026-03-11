# Engagement Automation & Notifications

This system provides automated email notifications to drive engagement and guide users through their subscription lifecycle.

## Notification Types

### 1. Trial Expiration Warnings (Days 5, 6, 7)
**Command:** `send_trial_warnings`
- Sent to users in active trial
- 3 warning emails on days 5, 6, 7 before expiration
- Directs users to pricing page
- Personalizes by language

**Schedule:** Daily at 8:00 AM
```bash
python manage.py send_trial_warnings
```

### 2. Inactivity Reminders (7+ days no chat)
**Command:** `send_inactivity_reminders`
- Sent to paid users with no conversations in 7+ days
- Encourages return to platform
- Links to chat module
- Personalizes by language and user name

**Arguments:**
- `--days`: threshold in days (default: 7)
- `--min-conversations`: minimum to qualify (default: 1)

**Schedule:** Daily at 9:00 AM
```bash
python manage.py send_inactivity_reminders --days 7
```

### 3. Journal Reminders (No entry today)
**Command:** `send_journal_reminders`
- Sent to active paid users with no journal entry today
- Encourages self-reflection
- Suggests 5-minute journaling
- Available to BASIC, PREMIUM, VIP tiers

**Arguments:**
- `--skip-free`: exclude free tier users

**Schedule:** Daily at 8:30 AM
```bash
python manage.py send_journal_reminders
```

### 4. Goal Reminders (Goals saved in profile)
**Command:** `send_goal_reminders`
- Sent to active users with `profile.keywords.goals`
- Fires only when the user has saved goals and has not chatted or journaled recently
- Uses the stored goal list to personalize the email
- Deduplicated to one send per user per day

**Arguments:**
- `--days-since-activity`: inactivity window before sending (default: 2)
- `--skip-free`: exclude free tier users

**Schedule:** Daily at 6:00 PM
```bash
python manage.py send_goal_reminders --days-since-activity 2
```

### 5. Daily Planning Reminders (Morning prompt)
**Command:** `send_daily_plan_reminders`
- Sent to engaged users (1+ past conversations)
- Morning planning prompt for the day
- Links to coaching module
- Only to users with prior platform usage

**Arguments:**
- `--skip-free`: exclude free tier
- `--min-conversations`: minimum to qualify (default: 1)

**Schedule:** Daily at 7:00 AM
```bash
python manage.py send_daily_plan_reminders
```

### 6. Wellbeing Check-in Reminders (No check-in today)
**Command:** `send_wellbeing_reminders`
- Sent to active paid users with no wellbeing check-in today
- 1-minute mood/energy/status capture
- Helps AI understand user better
- Personalizes by language

**Arguments:**
- `--skip-free`: exclude free tier

**Schedule:** Daily at 10:00 AM
```bash
python manage.py send_wellbeing_reminders
```

### 7. Upgrade Recommendations (Behavioral triggers)
**Command:** `send_upgrade_recommendations`
- Sent to BASIC and TRIAL users showing high engagement
- Triggers:
  - 5+ journal entries → recommend PREMIUM reports
  - 3+ conversations → recommend PREMIUM analytics
- Only to recently active users (3+ days)

**Arguments:**
- `--min-journal-entries`: threshold (default: 5)
- `--min-conversations`: threshold (default: 3)
- `--days-active`: recent activity window (default: 3)

**Schedule:** Daily at 2:00 PM
```bash
python manage.py send_upgrade_recommendations
```

## Cron Configuration

Add to `/etc/crontab` or use Docker/Kubernetes CronJob:

```bash
# 7:00 AM - Daily planning reminders
0 7 * * * cd /app && python manage.py send_daily_plan_reminders

# 5:00 AM - Trial warnings
0 5 * * * cd /app && python manage.py send_trial_warnings

# 8:00 AM - Journal reminders
0 8 * * * cd /app && python manage.py send_journal_reminders

# 9:00 AM - Inactivity reminders
0 9 * * * cd /app && python manage.py send_inactivity_reminders

# 10:00 AM - Wellbeing check-in reminders
0 10 * * * cd /app && python manage.py send_wellbeing_reminders

# 6:00 PM - Goal reminders
0 18 * * * cd /app && python manage.py send_goal_reminders

# 2:00 PM - Upgrade recommendations
0 14 * * * cd /app && python manage.py send_upgrade_recommendations
```

## Docker / Kubernetes

For containerized deployments, use a sidecar CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: doisense-notifications
spec:
  schedule: "0 5,7,8,9,10,14,18 * * *"  # Run at 5, 7, 8, 9, 10, 14, 18 (UTC)
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: notifications
            image: doisense/backend:latest
            command:
            - /bin/sh
            - -c
            - |
              case $(date +%H) in
                05) python manage.py send_trial_warnings ;;
                07) python manage.py send_daily_plan_reminders ;;
                08) python manage.py send_journal_reminders ;;
                09) python manage.py send_inactivity_reminders ;;
                10) python manage.py send_wellbeing_reminders ;;
                14) python manage.py send_upgrade_recommendations ;;
                18) python manage.py send_goal_reminders ;;
              esac
            env:
            - name: DJANGO_SETTINGS_MODULE
              value: config.settings
          restartPolicy: OnFailure
```

## Email Configuration

All notifications require SMTP configuration in Django admin:
1. Go to **Core > System Config**
2. Configure under **Contact & Email** section:
   - Email Host (e.g., smtp.gmail.com)
   - Email Port (e.g., 587 for TLS)
   - Email User / Password
   - Use TLS or SSL
   - From Email (e.g., noreply@doisense.app)

## Testing

Test a single notification type:

```bash
# Test with specific parameters
python manage.py send_inactivity_reminders --days 3 --min-conversations 1

# Test goal reminders
python manage.py send_goal_reminders --days-since-activity 1

# View what would be sent (with logging)
python manage.py send_daily_plan_reminders --verbosity 3
```

## Monitoring

Monitor notification delivery with logs:

```bash
# Check Django logs for errors
tail -f /var/log/doisense/django.log | grep -i notification

# Count sent notifications
grep "Sent.*reminder" /var/log/doisense/django.log | wc -l
```

## Language Support

Notifications are automatically sent in user's language:
- Romanian (ro)
- English (en)
- Default language follows user.language field

## Delivery Safety

- Daily notifications are deduplicated per user and day.
- Trial warnings are deduplicated by both day and warning stage (day 5/6/7).
- Upgrade recommendations are deduplicated by trigger reason.
- Delivery logs are stored in `core_notificationdelivery` and visible in Django admin.

## Customization

To customize notification content:
1. Edit `/backend/core/notifications.py`
2. Modify message body/subject in relevant `send_*` function
3. Redeploy backend

To customize timing:
1. Modify cron schedule
2. Adjust `--days`, `--days-since-activity`, and `--min-*` parameters in commands
3. Restart cron service

## Best Practices

1. **Stagger sends:** Don't send all at 8:00 AM, use different hours
2. **Monitor bounce rates:** Check email delivery logs
3. **Respect preferences:** Add unsubscribe link (future enhancement)
4. **Test first:** Run on small user segment before full rollout
5. **Track metrics:** Monitor open/click rates via email provider
