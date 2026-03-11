# INTEGRARE BACKEND - ORCHESTRATOR AI CU VERIFICARE DB

## Overview

Sistemul ORCHESTRATOR AI funcționează în trei straturi:

1. **AI Layer** (`orchestrator.txt`) - Generează răspunsuri JSON cu `save_to_db` flags
2. **Orchestration Layer** (`prompt_builder.py`) - Validează și routează datele
3. **Database Layer** - Salvează datele cu error handling și transaction management

---

## 1. SETUP - ÎNCĂRCAREA PROMPTULUI

### În `ai/views.py` sau `ai/router.py`:

```python
from ai.prompt_builder import (
    get_orchestrator_system_prompt,
    validate_save_to_db,
    extract_save_to_db_fields,
    build_db_save_request,
)
from ai.models import ConversationTemplate
import json

@router.post("/chat/send")
def chat_send(request, payload: dict):
    """Handle chat messages with orchestrator system prompt."""
    user = request.user
    message = payload.get("message", "").strip()
    language = getattr(user, "language", "en")
    
    # 1. LOAD ORCHESTRATOR PROMPT
    system_prompt = get_orchestrator_system_prompt(user, language)
    
    # 2. CALL AI WITH ORCHESTRATOR SYSTEM PROMPT
    ai_response = call_ai_api(
        system_prompt=system_prompt,
        user_message=message,
        model="gpt-4"  # or your model
    )
    
    # 3. PARSE RESPONSE AS JSON
    try:
        response_json = json.loads(ai_response)
    except json.JSONDecodeError:
        return {"error": "Invalid AI response format", "raw": ai_response}
    
    # 4. VALIDATE save_to_db BASED ON PACKAGE
    response_json = validate_save_to_db(user, response_json)
    
    # 5. BUILD DB SAVE REQUEST
    save_request = build_db_save_request(
        user_id=user.id,
        response_json=response_json,
        original_message=message
    )
    
    # 6. PROCESS SAVES (with error handling)
    save_results = process_db_saves(user, save_request)
    
    # 7. RETURN RESPONSE TO FRONTEND
    return {
        "response": response_json.get("response", ""),
        "response_type": response_json.get("response_type", "response"),
        "save_status": save_results,
        "full_response": response_json  # Optional: for debugging
    }
```

---

## 2. DATABASE SAVE PROCESSING

### Create `ai/db_operations.py`:

```python
from django.db import transaction
from datetime import datetime
from ai.models import Conversation, EmotionalAnalysis, WellnessMetric, Question
from typing import Dict, Any, List

def process_db_saves(user, save_request: Dict[str, Any]) -> Dict[str, str]:
    """Process all database save operations with error handling.
    
    Returns status dict indicating success/failure for each operation.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "operations": [],
        "errors": []
    }
    
    try:
        with transaction.atomic():
            for operation in save_request.get("operations", []):
                op_type = operation.get("type")
                op_data = operation.get("data", {})
                
                try:
                    if op_type == "conversation":
                        _save_conversation(user, op_data)
                        results["operations"].append({
                            "type": "conversation",
                            "status": "success"
                        })
                    
                    elif op_type == "emotional_tags":
                        _save_emotional_tags(user, op_data)
                        results["operations"].append({
                            "type": "emotional_tags",
                            "status": "success"
                        })
                    
                    elif op_type == "wellness_metrics":
                        _save_wellness_metrics(user, op_data)
                        results["operations"].append({
                            "type": "wellness_metrics",
                            "status": "success"
                        })
                    
                    elif op_type == "questions_generated":
                        _save_questions(user, op_data)
                        results["operations"].append({
                            "type": "questions_generated",
                            "status": "success"
                        })
                    
                    elif op_type == "analysis_summary":
                        _save_analysis(user, op_data)
                        results["operations"].append({
                            "type": "analysis_summary",
                            "status": "success"
                        })
                    
                    elif op_type == "daily_report":
                        _save_daily_report(user, op_data)
                        results["operations"].append({
                            "type": "daily_report",
                            "status": "success"
                        })
                    
                    elif op_type == "weekly_report":
                        _save_weekly_report(user, op_data)
                        results["operations"].append({
                            "type": "weekly_report",
                            "status": "success"
                        })
                    
                    elif op_type == "monthly_report":
                        _save_monthly_report(user, op_data)
                        results["operations"].append({
                            "type": "monthly_report",
                            "status": "success"
                        })
                    
                    elif op_type == "typology_update":
                        _save_typology(user, op_data)
                        results["operations"].append({
                            "type": "typology_update",
                            "status": "success"
                        })
                
                except Exception as e:
                    results["errors"].append({
                        "operation": op_type,
                        "error": str(e)
                    })
                    results["operations"].append({
                        "type": op_type,
                        "status": "failed",
                        "error": str(e)
                    })
    
    except transaction.TransactionManagementError as e:
        results["errors"].append({
            "transaction": "atomic_transaction_failed",
            "error": str(e)
        })
    
    return results


def _save_conversation(user, data: Dict) -> None:
    """Save conversation message and AI response."""
    Conversation.objects.create(
        user=user,
        user_message=data.get("message", ""),
        ai_response=data.get("response", ""),
        response_type=data.get("response_type", "response")
    )


def _save_emotional_tags(user, data: Dict) -> None:
    """Save detected emotions."""
    from profiles.models import UserProfile
    
    profile = user.profile
    profile.last_dominant_emotion = data.get("dominant_emotion")
    profile.secondary_emotions = data.get("secondary_emotions", [])
    profile.save()


def _save_wellness_metrics(user, data: Dict) -> None:
    """Save wellness scores (stress, energy, motivation)."""
    WellnessMetric.objects.create(
        user=user,
        stress_score=float(data.get("stress_score", 0)) if data.get("stress_score") else None,
        energy_score=float(data.get("energy_score", 0)) if data.get("energy_score") else None,
        motivation_score=float(data.get("motivation_score", 0)) if data.get("motivation_score") else None
    )


def _save_questions(user, data: Dict) -> None:
    """Save generated questions for tracking and avoiding repeats."""
    questions = data.get("questions", [])
    for q in questions:
        Question.objects.create(
            user=user,
            text=q.get("intrebare", ""),
            question_type=q.get("tip_intrebare", "open"),
            reason=q.get("motiv_generare", ""),
            priority=q.get("prioritate", "medium")
        )


def _save_analysis(user, data: Dict) -> None:
    """Save emotional analysis summary."""
    from ai.models import EmotionalAnalysis
    
    analysis = data.get("analysis", {})
    EmotionalAnalysis.objects.create(
        user=user,
        dominant_emotion=analysis.get("emotie_dominanta", ""),
        secondary_emotions=analysis.get("emotii_secundare", []),
        triggers=analysis.get("posibili_declansatori", []),
        stress_score=float(analysis.get("scoruri", {}).get("stres", 0)) if analysis.get("scoruri", {}).get("stres") else None,
        energy_score=float(analysis.get("scoruri", {}).get("energie", 0)) if analysis.get("scoruri", {}).get("energie") else None,
        motivation_score=float(analysis.get("scoruri", {}).get("motivatie", 0)) if analysis.get("scoruri", {}).get("motivatie") else None,
        observations=analysis.get("observatii", "")
    )


def _save_daily_report(user, data: Dict) -> None:
    """Save daily report."""
    from ai.models import DailyReport
    from datetime import date
    
    DailyReport.objects.update_or_create(
        user=user,
        date=date.today(),
        defaults={
            "summary": data.get("rezumat", ""),
            "highlights": data.get("highlights", []),
            "challenges": data.get("challenges", []),
            "recommendations": data.get("recomandari", [])
        }
    )


def _save_weekly_report(user, data: Dict) -> None:
    """Save weekly report."""
    from ai.models import WeeklyReport
    from datetime import datetime, timedelta
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    WeeklyReport.objects.update_or_create(
        user=user,
        week_start=week_start.date(),
        defaults={
            "summary": data.get("rezumat", ""),
            "trends": data.get("tendinte", []),
            "progress": data.get("progres", ""),
            "recommendations": data.get("recomandari", [])
        }
    )


def _save_monthly_report(user, data: Dict) -> None:
    """Save monthly report."""
    from ai.models import MonthlyReport
    from datetime import datetime
    
    today = datetime.now()
    
    MonthlyReport.objects.update_or_create(
        user=user,
        year=today.year,
        month=today.month,
        defaults={
            "summary": data.get("rezumat", ""),
            "trends": data.get("tendinte", []),
            "insights": data.get("insights", ""),
            "recommendations": data.get("recomandari", [])
        }
    )


def _save_typology(user, data: Dict) -> None:
    """Save/update emotional and behavioral typology."""
    from profiles.models import UserProfile
    
    profile = user.profile
    profile.emotional_typology = data.get("tipologie_emotionala", "")
    profile.behavioral_typology = data.get("tipologie_comportamentala", "")
    profile.typology_strengths = data.get("puncte_forte", [])
    profile.typology_vulnerabilities = data.get("vulnerabilitati", [])
    profile.typology_last_updated = datetime.now()
    profile.save()
```

---

## 3. MODELS NÉCESSAIRES

Ensure your models support the data structure:

```python
# ai/models.py
from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    user_message = models.TextField()
    ai_response = models.TextField()
    response_type = models.CharField(max_length=50, default="response")
    created_at = models.DateTimeField(auto_now_add=True)

class EmotionalAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emotional_analyses")
    dominant_emotion = models.CharField(max_length=100)
    secondary_emotions = models.JSONField(default=list)
    triggers = models.JSONField(default=list)
    stress_score = models.FloatField(null=True, blank=True)
    energy_score = models.FloatField(null=True, blank=True)
    motivation_score = models.FloatField(null=True, blank=True)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WellnessMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wellness_metrics")
    stress_score = models.FloatField(null=True, blank=True)
    energy_score = models.FloatField(null=True, blank=True)
    motivation_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    QUESTION_TYPES = [("open", "Open"), ("multiple_choice", "Multiple Choice"), ("rating", "Rating"), ("yes_no", "Yes/No")]
    PRIORITY_LEVELS = [("high", "High"), ("medium", "Medium"), ("low", "Low")]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="generated_questions")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    reason = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_reports")
    date = models.DateField(unique_for_date=True)
    summary = models.TextField()
    highlights = models.JSONField(default=list)
    challenges = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WeeklyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weekly_reports")
    week_start = models.DateField()
    summary = models.TextField()
    trends = models.JSONField(default=list)
    progress = models.TextField(blank=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MonthlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_reports")
    year = models.IntegerField()
    month = models.IntegerField()
    summary = models.TextField()
    trends = models.JSONField(default=list)
    insights = models.TextField(blank=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("user", "year", "month")
```

---

## 4. FLUX COMPLET - DE LA REQUEST LA RESPONSE

```
1. FRONTEND REQUEST
   POST /api/chat/send
   {
     "message": "Azi nu m-am simțit bine",
     "module": "wellness"
   }

2. BACKEND LOADS ORCHESTRATOR
   system_prompt = get_orchestrator_system_prompt(user)
   # → Includes user's package tier (BASIC/PREMIUM/VIP)

3. AI PROCESSES WITH ORCHESTRATOR
   response = call_ai_api(
     system_prompt=orchestrator_prompt,
     user_message="Azi nu m-am simțit bine"
   )

4. PARSE AI RESPONSE
   response_json = {
     "response": "Înțeleg...",
     "response_type": "response",
     "analysis": {...},
     "questions": [...],
     "save_to_db": {
       "conversations": true,
       "emotional_tags": true,
       "wellness_metrics": true,
       ...
     }
   }

5. VALIDATE AGAINST PACKAGE
   response_json = validate_save_to_db(user, response_json)
   # → For BASIC: daily_reports, weekly_reports, monthly_reports = false

6. BUILD DB SAVE REQUEST
   save_request = build_db_save_request(
     user_id=user.id,
     response_json=response_json,
     original_message="Azi nu m-am simțit bine"
   )

7. PROCESS SAVES WITH TRANSACTION
   save_results = process_db_saves(user, save_request)
   # → All operations in one atomic transaction
   # → Error handling per operation

8. RETURN RESPONSE TO FRONTEND
   return {
     "response": "Înțeleg...",
     "save_status": {
       "operations": [
         {"type": "conversation", "status": "success"},
         {"type": "emotional_tags", "status": "success"}
       ],
       "errors": []
     }
   }
```

---

## 5. ERROR HANDLING

### Eroare la Salvare - Retry Logic:

```python
def process_db_saves_with_retry(user, save_request, max_retries=3):
    """Process saves with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            return process_db_saves(user, save_request)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed - log and return error
                logger.error(f"Failed to save after {max_retries} attempts: {e}")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e),
                    "attempt": attempt + 1
                }
            # Retry after short delay
            time.sleep(2 ** attempt)
```

---

## 6. LOGGING ȘI MONITORING

```python
import logging

logger = logging.getLogger("ai_orchestrator")

def chat_send_with_logging(request, payload):
    """Add comprehensive logging."""
    user = request.user
    message = payload.get("message", "").strip()
    
    logger.info(f"Chat request from user {user.id}: {message[:50]}...")
    
    try:
        system_prompt = get_orchestrator_system_prompt(user)
        ai_response = call_ai_api(system_prompt=system_prompt, user_message=message)
        response_json = json.loads(ai_response)
        
        logger.info(f"AI response type: {response_json.get('response_type')}")
        
        response_json = validate_save_to_db(user, response_json)
        save_request = build_db_save_request(user.id, response_json, message)
        save_results = process_db_saves(user, save_request)
        
        if save_results.get("errors"):
            logger.warning(f"Save errors for user {user.id}: {save_results['errors']}")
        else:
            logger.info(f"All saves successful for user {user.id}")
        
        return {
            "response": response_json.get("response", ""),
            "save_status": save_results
        }
    
    except Exception as e:
        logger.error(f"Error in chat_send for user {user.id}: {e}", exc_info=True)
        return {"error": "Internal server error", "user_id": user.id}
```

---

## SUMMARY

- **orchestrator.txt** = Master AI instructions with save_to_db fields
- **prompt_builder.py** = Loads prompturi, validează după pachet, construiește save requests
- **db_operations.py** = Execută saves cu transaction management și error handling
- **Logging** = Track all operations for debugging și monitoring
- **Package Tiers** = Enforced automatically pe baza user subscription

Sistemul este *autonomous* → AI indică ce trebuie salvat → Backend salvează → Frontend primește status.
