from rest_framework import viewsets
from .models import Employer, Candidate, Recruiter, Interview, Feedback, FeatureUsage, SystemIssue
from .serializers import (
    EmployerSerializer, CandidateSerializer, RecruiterSerializer,
    InterviewSerializer, FeedbackSerializer, FeatureUsageSerializer, SystemIssueSerializer
)

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class RecruiterViewSet(viewsets.ModelViewSet):
    queryset = Recruiter.objects.all()
    serializer_class = RecruiterSerializer

class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class FeatureUsageViewSet(viewsets.ModelViewSet):
    queryset = FeatureUsage.objects.all()
    serializer_class = FeatureUsageSerializer

class SystemIssueViewSet(viewsets.ModelViewSet):
    queryset = SystemIssue.objects.all()
    serializer_class = SystemIssueSerializer

# Analytics Views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Case, When
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def engagement_metrics_view(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    interviews_started_today = Interview.objects.filter(start_time__date=today).count()
    interviews_completed_today = Interview.objects.filter(end_time__date=today, status='Completed').count()

    interviews_started_this_week = Interview.objects.filter(start_time__date__gte=start_of_week).count()
    interviews_completed_this_week = Interview.objects.filter(end_time__date__gte=start_of_week, status='Completed').count()

    interviews_started_this_month = Interview.objects.filter(start_time__date__gte=start_of_month).count()
    interviews_completed_this_month = Interview.objects.filter(end_time__date__gte=start_of_month, status='Completed').count()
    
    # Average time per interview in minutes
    # Ensure end_time and start_time are not null and end_time is greater than start_time
    completed_interviews_with_duration = Interview.objects.filter(
        status='Completed', 
        end_time__isnull=False, 
        start_time__isnull=False,
        end_time__gt=F('start_time')
    ).annotate(
        duration=ExpressionWrapper(F('end_time') - F('start_time'), output_field=fields.DurationField())
    )
    
    average_duration_seconds = completed_interviews_with_duration.aggregate(avg_duration=Avg('duration'))['avg_duration']
    average_time_per_interview_minutes = (average_duration_seconds.total_seconds() / 60) if average_duration_seconds else 0

    total_interviews = Interview.objects.count()
    abandoned_interviews = Interview.objects.filter(abandoned=True).count()
    interview_abandonment_rate = (abandoned_interviews / total_interviews * 100) if total_interviews > 0 else 0

    data = {
        'interviews_started_today': interviews_started_today,
        'interviews_completed_today': interviews_completed_today,
        'interviews_started_this_week': interviews_started_this_week,
        'interviews_completed_this_week': interviews_completed_this_week,
        'interviews_started_this_month': interviews_started_this_month,
        'interviews_completed_this_month': interviews_completed_this_month,
        'average_time_per_interview_minutes': round(average_time_per_interview_minutes, 2),
        'interview_abandonment_rate': round(interview_abandonment_rate, 2),
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_progression_view(request):
    status_choices = Interview.STATUS_CHOICES
    progression_data = {}
    
    # Get counts for each stage
    stage_counts = Interview.objects.values('status').annotate(count=Count('status')).order_by('status')
    
    # Convert to a dictionary for easier access
    counts_dict = {item['status']: item['count'] for item in stage_counts}

    # Ensure all defined stages are present in the output, even if count is 0
    for status_key, status_display in status_choices:
        progression_data[status_key] = {
            'count': counts_dict.get(status_key, 0),
            'display_name': status_display
        }

    # Calculate drop-off rates (example: Invited -> Started)
    # This is a simplified example; a full funnel would require ordering and sequential calculation
    
    total_invited = progression_data.get('Invited', {}).get('count', 0)
    
    # Drop-off percentages
    # This logic assumes a linear progression. A more robust solution might need explicit stage ordering.
    previous_stage_count = total_invited # Start with 'Invited' or the first logical stage
    
    # Order of stages for drop-off calculation (must match STATUS_CHOICES order or be defined explicitly)
    # For simplicity, let's use the order from STATUS_CHOICES if it makes sense for the funnel
    ordered_stages = [s[0] for s in status_choices] 

    for i in range(len(ordered_stages)):
        current_stage_key = ordered_stages[i]
        current_stage_data = progression_data.get(current_stage_key)

        if not current_stage_data: # Should not happen if all stages are initialized
            continue

        current_count = current_stage_data.get('count', 0)
        
        if i > 0: # Cannot calculate drop-off for the first stage
            prev_stage_key = ordered_stages[i-1]
            # Get the count of the *actual* previous stage in our calculation sequence
            # This is important if some stages in STATUS_CHOICES have 0 candidates and aren't "previous_stage_count"
            actual_previous_count = progression_data.get(prev_stage_key, {}).get('count', 0)
            
            if actual_previous_count > 0:
                drop_off_from_previous = ((actual_previous_count - current_count) / actual_previous_count * 100)
                current_stage_data['drop_off_from_previous_stage_percentage'] = round(drop_off_from_previous, 2)
            else:
                current_stage_data['drop_off_from_previous_stage_percentage'] = 0 # Or None, or 'N/A'
        else: # First stage in our defined order
             current_stage_data['drop_off_from_previous_stage_percentage'] = 0 # No drop-off for the first stage


    return Response(progression_data)
