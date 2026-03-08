from django.db import models

from core.validators import validate_language


class GuidedProgram(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=2, validators=[validate_language])
    active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        db_table = "programs_guidedprogram"

    def __str__(self):
        return self.title


class GuidedProgramDay(models.Model):
    program = models.ForeignKey(
        GuidedProgram, on_delete=models.CASCADE, related_name="days"
    )
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    question = models.TextField(blank=True)
    ai_prompt = models.TextField(blank=True)

    class Meta:
        db_table = "programs_guidedprogramday"
        ordering = ["day_number"]
        unique_together = [("program", "day_number")]

    def __str__(self):
        return f"{self.program.title} - Day {self.day_number}"
