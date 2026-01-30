from django.db import models
from core.models import Interview

class InterviewResponse(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='responses')
    question_text = models.TextField()
    transcription = models.TextField()

    # Individual scores (1-10)
    relevance_score = models.FloatField(default=0.0)
    technical_depth_score = models.FloatField(default=0.0)
    clarity_score = models.FloatField(default=0.0)
    communication_score = models.FloatField(default=0.0)

    # Final production-ready score
    final_score = models.FloatField(default=0.0)

    # AI Feedback
    ai_feedback = models.TextField(blank=True, null=True)

    # Anti-cheating flags
    tab_switch_count = models.IntegerField(default=0)
    is_suspicious = models.BooleanField(default=False)
    cheating_flags = models.TextField(blank=True, null=True) # JSON or comma-separated

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.interview.candidate} - {self.question_text[:30]}..."
