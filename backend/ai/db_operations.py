"""Database operations for AI orchestrator.

Handles all data persistence with transaction management, error handling,
and proper validation of save_to_db flags from AI responses.
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
import logging

from ai.models import Conversation, EmotionalAnalysis, WellnessMetric, Question
from profiles.models import UserProfile

logger = logging.getLogger("ai_orchestrator")


def process_db_saves(user, save_request: Dict[str, Any]) -> Dict[str, Any]:
    """Process all database save operations with error handling.
    
    This is the main orchestrator for database persistence. It processes
    a structured save_request and returns detailed status for each operation.
    
    Args:
        user: Django User object
        save_request: Dict with structure:
            {
                "user_id": int,
                "timestamp": str (optional),
                "operations": [
                    {
                        "type": str,
                        "data": dict
                    }
                ]
            }
    
    Returns:
        Dict with:
            - timestamp: ISO format datetime
            - operations: List of operation results
            - errors: List of errors encountered
            - total_operations: int
            - successful_operations: int
            - failed_operations: int
    """
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "operations": [],
        "errors": [],
        "total_operations": 0,
        "successful_operations": 0,
        "failed_operations": 0
    }
    
    operations = save_request.get("operations", [])
    results["total_operations"] = len(operations)
    
    if not operations:
        logger.debug(f"No operations to save for user {user.id}")
        return results
    
    try:
        with transaction.atomic():
            for operation in operations:
                op_type = operation.get("type")
                op_data = operation.get("data", {})
                
                operation_result = {
                    "type": op_type,
                    "status": "pending",
                    "message": ""
                }
                
                try:
                    if op_type == "conversation":
                        _save_conversation(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved conversation for user {user.id}")
                    
                    elif op_type == "emotional_tags":
                        _save_emotional_tags(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved emotional tags for user {user.id}")
                    
                    elif op_type == "wellness_metrics":
                        _save_wellness_metrics(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved wellness metrics for user {user.id}")
                    
                    elif op_type == "questions_generated":
                        _save_questions(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved generated questions for user {user.id}")
                    
                    elif op_type == "analysis_summary":
                        _save_analysis(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved analysis summary for user {user.id}")
                    
                    elif op_type == "daily_report":
                        _save_daily_report(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved daily report for user {user.id}")
                    
                    elif op_type == "weekly_report":
                        _save_weekly_report(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved weekly report for user {user.id}")
                    
                    elif op_type == "monthly_report":
                        _save_monthly_report(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved monthly report for user {user.id}")
                    
                    elif op_type == "typology_update":
                        _save_typology(user, op_data)
                        operation_result["status"] = "success"
                        results["successful_operations"] += 1
                        logger.debug(f"Saved typology update for user {user.id}")
                    
                    else:
                        operation_result["status"] = "unknown"
                        operation_result["message"] = f"Unknown operation type: {op_type}"
                        logger.warning(f"Unknown operation type: {op_type}")
                
                except Exception as e:
                    operation_result["status"] = "failed"
                    operation_result["message"] = str(e)
                    results["failed_operations"] += 1
                    results["errors"].append({
                        "operation": op_type,
                        "error": str(e),
                        "data_sample": str(op_data)[:100]
                    })
                    logger.error(f"Failed to save {op_type} for user {user.id}: {e}", exc_info=True)
                
                results["operations"].append(operation_result)
    
    except transaction.TransactionManagementError as e:
        results["errors"].append({
            "type": "transaction_error",
            "error": str(e)
        })
        logger.error(f"Transaction error for user {user.id}: {e}", exc_info=True)
        results["status"] = "transaction_failed"
    
    except Exception as e:
        results["errors"].append({
            "type": "unknown_error",
            "error": str(e)
        })
        logger.error(f"Unexpected error in process_db_saves for user {user.id}: {e}", exc_info=True)
        results["status"] = "unknown_error"
    
    return results


# ============================================================================
# OPERATION HANDLERS
# ============================================================================

def _save_conversation(user, data: Dict[str, Any]) -> None:
    """Save conversation message and AI response.
    
    Required data fields:
        - message: str (user message)
        - response: str (AI response)
        - response_type: str (type of response)
    """
    Conversation.objects.create(
        user=user,
        user_message=data.get("message", ""),
        ai_response=data.get("response", ""),
        response_type=data.get("response_type", "response")
    )


def _save_emotional_tags(user, data: Dict[str, Any]) -> None:
    """Save detected emotions to user profile.
    
    Required data fields:
        - dominant_emotion: str
        - secondary_emotions: list
    """
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.last_dominant_emotion = data.get("dominant_emotion", "")
    profile.secondary_emotions = data.get("secondary_emotions", [])
    profile.last_emotion_updated = timezone.now()
    profile.save(update_fields=[
        'last_dominant_emotion',
        'secondary_emotions',
        'last_emotion_updated'
    ])


def _save_wellness_metrics(user, data: Dict[str, Any]) -> None:
    """Save wellness scores (stress, energy, motivation).
    
    Required data fields:
        - stress_score: float (0-100, optional)
        - energy_score: float (0-100, optional)
        - motivation_score: float (0-100, optional)
    """
    stress = data.get("stress_score")
    energy = data.get("energy_score")
    motivation = data.get("motivation_score")
    
    # Validate scores are in range 0-100
    if stress is not None:
        stress = float(stress) if stress else None
        if stress and (stress < 0 or stress > 100):
            raise ValueError(f"Stress score out of range: {stress}")
    
    if energy is not None:
        energy = float(energy) if energy else None
        if energy and (energy < 0 or energy > 100):
            raise ValueError(f"Energy score out of range: {energy}")
    
    if motivation is not None:
        motivation = float(motivation) if motivation else None
        if motivation and (motivation < 0 or motivation > 100):
            raise ValueError(f"Motivation score out of range: {motivation}")
    
    WellnessMetric.objects.create(
        user=user,
        stress_score=stress,
        energy_score=energy,
        motivation_score=motivation
    )


def _save_questions(user, data: Dict[str, Any]) -> None:
    """Save generated questions for tracking and avoiding repeats.
    
    Required data fields:
        - questions: list of dicts with:
            - intrebare: str (question text)
            - tip_intrebare: str (open, multiple_choice, rating, yes_no)
            - motiv_generare: str (reason for generation)
            - prioritate: str (high, medium, low)
    """
    questions = data.get("questions", [])
    
    for q in questions:
        question_text = q.get("intrebare", "").strip()
        if not question_text:
            logger.warning(f"Empty question text for user {user.id}, skipping")
            continue
        
        question_type = q.get("tip_intrebare", "open")
        # Validate question type
        valid_types = ["open", "multiple_choice", "rating", "yes_no"]
        if question_type not in valid_types:
            question_type = "open"
        
        Question.objects.create(
            user=user,
            text=question_text,
            question_type=question_type,
            reason=q.get("motiv_generare", ""),
            priority=q.get("prioritate", "medium")
        )


def _save_analysis(user, data: Dict[str, Any]) -> None:
    """Save emotional analysis summary.
    
    Required data fields (nested under 'analysis'):
        - emotie_dominanta: str
        - emotii_secundare: list
        - posibili_declansatori: list
        - scoruri: dict with stres, energie, motivatie
        - observatii: str
    """
    analysis = data.get("analysis", {})
    
    scores = analysis.get("scoruri", {})
    stress = scores.get("stres")
    energy = scores.get("energie")
    motivation = scores.get("motivatie")
    
    # Convert to float and validate
    if stress:
        stress = float(stress)
    if energy:
        energy = float(energy)
    if motivation:
        motivation = float(motivation)
    
    EmotionalAnalysis.objects.create(
        user=user,
        dominant_emotion=analysis.get("emotie_dominanta", ""),
        secondary_emotions=analysis.get("emotii_secundare", []),
        triggers=analysis.get("posibili_declansatori", []),
        stress_score=stress,
        energy_score=energy,
        motivation_score=motivation,
        observations=analysis.get("observatii", "")
    )


def _save_daily_report(user, data: Dict[str, Any]) -> None:
    """Save or update daily report.
    
    Required data fields:
        - rezumat: str
        - highlights: list
        - challenges: list
        - recomandari: list
    """
    from ai.models import DailyReport
    
    today = date.today()
    
    DailyReport.objects.update_or_create(
        user=user,
        date=today,
        defaults={
            "summary": data.get("rezumat", ""),
            "highlights": data.get("highlights", []),
            "challenges": data.get("challenges", []),
            "recommendations": data.get("recomandari", [])
        }
    )


def _save_weekly_report(user, data: Dict[str, Any]) -> None:
    """Save or update weekly report.
    
    Required data fields:
        - rezumat: str
        - tendinte: list
        - progres: str
        - recomandari: list
    """
    from ai.models import WeeklyReport
    
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


def _save_monthly_report(user, data: Dict[str, Any]) -> None:
    """Save or update monthly report.
    
    Required data fields:
        - rezumat: str
        - tendinte: list
        - insights: str
        - recomandari: list
    """
    from ai.models import MonthlyReport
    
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


def _save_typology(user, data: Dict[str, Any]) -> None:
    """Save/update emotional and behavioral typology (VIP only).
    
    Required data fields:
        - tipologie_emotionala: str
        - tipologie_comportamentala: str
        - puncte_forte: list
        - vulnerabilitati: list
    """
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.emotional_typology = data.get("tipologie_emotionala", "")
    profile.behavioral_typology = data.get("tipologie_comportamentala", "")
    profile.typology_strengths = data.get("puncte_forte", [])
    profile.typology_vulnerabilities = data.get("vulnerabilitati", [])
    profile.typology_last_updated = timezone.now()
    profile.save(update_fields=[
        'emotional_typology',
        'behavioral_typology',
        'typology_strengths',
        'typology_vulnerabilities',
        'typology_last_updated'
    ])


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def process_db_saves_with_retry(user, save_request: Dict[str, Any],
                                max_retries: int = 3) -> Dict[str, Any]:
    """Process saves with retry logic for transient failures.
    
    Useful for handling temporary database connection issues.
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return process_db_saves(user, save_request)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed
                logger.error(
                    f"Failed to save after {max_retries} attempts for user {user.id}: {e}"
                )
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e),
                    "attempt": attempt + 1,
                    "total_attempts": max_retries,
                    "operations": [],
                    "errors": [{"error": str(e), "attempt": attempt + 1}]
                }
            
            # Retry after exponential backoff
            wait_time = 2 ** attempt
            logger.info(f"Retrying save for user {user.id} after {wait_time}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "failed",
        "error": "Max retries exceeded"
    }


def get_save_status_summary(save_results: Dict[str, Any]) -> str:
    """Generate human-readable summary of save results."""
    total = save_results.get("total_operations", 0)
    successful = save_results.get("successful_operations", 0)
    failed = save_results.get("failed_operations", 0)
    
    if failed == 0:
        return f"✓ All {successful} operations saved successfully"
    else:
        return f"⚠ {successful}/{total} operations saved, {failed} failed"
