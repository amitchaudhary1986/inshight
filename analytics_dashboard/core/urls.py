from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployerViewSet, CandidateViewSet, RecruiterViewSet,
    InterviewViewSet, FeedbackViewSet, FeatureUsageViewSet, SystemIssueViewSet,
    engagement_metrics_view, candidate_progression_view
)

router = DefaultRouter()
router.register(r'employers', EmployerViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'recruiters', RecruiterViewSet)
router.register(r'interviews', InterviewViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'featureusage', FeatureUsageViewSet)
router.register(r'systemissues', SystemIssueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/engagement/', engagement_metrics_view, name='engagement-metrics'),
    path('analytics/candidate-progression/', candidate_progression_view, name='candidate-progression'),
]
