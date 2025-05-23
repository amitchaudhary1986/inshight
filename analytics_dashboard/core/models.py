from django.db import models

class Employer(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True, null=True)
    consistently_flags_inaccurate_ai = models.BooleanField(default=False)
    uses_scoring = models.BooleanField(default=True)
    reviews_results = models.BooleanField(default=True)
    total_interviews_conducted = models.IntegerField(default=0)
    total_hires = models.IntegerField(default=0)
    time_saved_vs_traditional = models.DurationField(blank=True, null=True)
    roi_signals = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255) # For heatmap
    current_stage = models.CharField(max_length=100) # Invited, Started, etc.

    def __str__(self):
        return self.name

class Recruiter(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Interview(models.Model):
    STATUS_CHOICES = [
        ('Invited', 'Invited'),
        ('Started', 'Started'),
        ('Completed', 'Completed'),
        ('Shortlisted', 'Shortlisted'),
        ('Selected', 'Selected'),
    ]
    DEVICE_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Mobile', 'Mobile'),
        ('Tablet', 'Tablet'),
    ]
    BROWSER_CHOICES = [
        ('Chrome', 'Chrome'),
        ('Firefox', 'Firefox'),
        ('Safari', 'Safari'),
        ('Edge', 'Edge'),
        ('Other', 'Other'),
    ]
    PLATFORM_CHOICES = [
        ('Web', 'Web'),
        ('iOS', 'iOS'),
        ('Android', 'Android'),
    ]
    INTERVIEW_TYPE_CHOICES = [
        ('Technical', 'Technical'),
        ('Behavioral', 'Behavioral'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    abandoned = models.BooleanField(default=False)
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES)
    browser_type = models.CharField(max_length=20, choices=BROWSER_CHOICES)
    platform_type = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    questions_used = models.TextField() # JSON or comma-separated
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)

    def __str__(self):
        return f"Interview for {self.candidate} with {self.employer}"

class Feedback(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    rating = models.IntegerField() # 1-5 or 1-10
    text = models.TextField() # For sentiment analysis, keywords
    ai_flagged_inaccurate = models.BooleanField(default=False) # If employer flagged
    complaint_raised = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback for Interview {self.interview.id}"

class FeatureUsage(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    feature_name = models.CharField(max_length=255) # e.g., deep_interview_scoring
    last_used = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.employer} - {self.feature_name}"

class SystemIssue(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Issue for {self.employer} reported at {self.reported_at}"
