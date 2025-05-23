from rest_framework import serializers
from .models import Employer, Candidate, Recruiter, Interview, Feedback, FeatureUsage, SystemIssue

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = '__all__'

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class FeatureUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureUsage
        fields = '__all__'

class SystemIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemIssue
        fields = '__all__'
