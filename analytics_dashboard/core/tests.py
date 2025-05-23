from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Interview, Employer, Candidate, Recruiter
from django.utils import timezone
from django.db.models import F # Import F expression
from datetime import timedelta, time
from rest_framework.authtoken.models import Token

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.employer = Employer.objects.create(name='Test Employer Inc.')
        self.candidate = Candidate.objects.create(name='Test Candidate', email='candidate@example.com', location='Test Location', current_stage='Invited')
        self.recruiter = Recruiter.objects.create(name='Test Recruiter', email='recruiter@example.com')
        
        self.today = timezone.now().date()
        self.start_of_today = timezone.make_aware(timezone.datetime.combine(self.today, time.min))
        self.middle_of_today = timezone.make_aware(timezone.datetime.combine(self.today, time(12,0,0)))
        self.end_of_today = timezone.make_aware(timezone.datetime.combine(self.today, time.max))

        self.yesterday = self.today - timedelta(days=1)
        self.start_of_week = self.today - timedelta(days=self.today.weekday())
        self.start_of_month = self.today.replace(day=1)


class EngagementMetricsAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Test Data for Engagement Metrics

        # Interview 1: Completed Today, 30 mins duration
        Interview.objects.create(
            status='Completed',
            start_time=self.middle_of_today - timedelta(minutes=30),
            end_time=self.middle_of_today,
            abandoned=False,
            device_type='Desktop', browser_type='Chrome', platform_type='Web', interview_type='Technical',
            questions_used='Q1,Q2', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )

        # Interview 2: Started Today, not completed
        Interview.objects.create(
            status='Started',
            start_time=self.middle_of_today - timedelta(hours=1),
            end_time=self.middle_of_today - timedelta(hours=1), # end_time might be same as start for 'Started' if not updated
            abandoned=False,
            device_type='Mobile', browser_type='Safari', platform_type='iOS', interview_type='Behavioral',
            questions_used='Q3', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )
        
        # Interview 3: Completed this week (but not today), 60 mins duration
        interview_day_this_week = self.start_of_week if self.start_of_week != self.today else self.start_of_week + timedelta(days=1)
        if interview_day_this_week >= self.today : # ensure it's not in the future and not today
            interview_day_this_week = self.today - timedelta(days=1) if self.today > self.start_of_week else self.start_of_week
            if interview_day_this_week == self.today and self.start_of_week == self.today : # if today is monday
                 interview_day_this_week = self.start_of_week # no change, can't create interview in past if week started today

        # Ensure interview_day_this_week is not today for this specific test case
        if interview_day_this_week == self.today :
             # If start_of_week is today (e.g. Monday), this interview cannot be "this week but not today" and in the past.
             # So, we only create it if it's possible to have such a day.
             if self.today > self.start_of_week:
                interview_time_this_week = timezone.make_aware(timezone.datetime.combine(interview_day_this_week, time(10,0,0)))
                Interview.objects.create(
                    status='Completed',
                    start_time=interview_time_this_week,
                    end_time=interview_time_this_week + timedelta(minutes=60),
                    abandoned=False, device_type='Desktop', browser_type='Chrome', platform_type='Web', interview_type='Technical',
                    questions_used='Q1,Q2', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
                )
        else: # Only create if interview_day_this_week is valid and not today
            interview_time_this_week = timezone.make_aware(timezone.datetime.combine(interview_day_this_week, time(10,0,0)))
            Interview.objects.create(
                status='Completed',
                start_time=interview_time_this_week,
                end_time=interview_time_this_week + timedelta(minutes=60),
                abandoned=False, device_type='Desktop', browser_type='Chrome', platform_type='Web', interview_type='Technical',
                questions_used='Q1,Q2', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
            )


        # Interview 4: Abandoned
        Interview.objects.create(
            status='Started', # Abandoned interviews might still be in 'Started' or a custom 'Abandoned' status
            start_time=self.middle_of_today - timedelta(days=2), # Some time ago
            end_time=self.middle_of_today - timedelta(days=2), 
            abandoned=True,
            device_type='Desktop', browser_type='Firefox', platform_type='Web', interview_type='Technical',
            questions_used='Q1', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )

        # Interview 5: Completed this month (but not this week or today), 45 mins
        interview_day_this_month = self.start_of_month
        # Ensure it's not today and not in the current week
        if interview_day_this_month < self.start_of_week and interview_day_this_month < self.today :
            interview_time_this_month = timezone.make_aware(timezone.datetime.combine(interview_day_this_month, time(11,0,0)))
            Interview.objects.create(
                status='Completed',
                start_time=interview_time_this_month,
                end_time=interview_time_this_month + timedelta(minutes=45),
                abandoned=False, device_type='Tablet', browser_type='Chrome', platform_type='Android', interview_type='Behavioral',
                questions_used='Q4,Q5', employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
            )
        
        self.engagement_url = reverse('engagement-metrics')

    def test_get_engagement_metrics_unauthenticated(self):
        self.client.credentials() # Clear authentication
        response = self.client.get(self.engagement_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_engagement_metrics_authenticated(self):
        response = self.client.get(self.engagement_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Expected values based on setUp data
        # interviews_started_today: Interview 1, Interview 2 = 2
        # interviews_completed_today: Interview 1 = 1
        # interviews_started_this_week: Interview 1, Interview 2 (+ Interview 3 if it ran)
        # interviews_completed_this_week: Interview 1 (+ Interview 3 if it ran)
        # interviews_started_this_month: Interview 1, Interview 2 (+ Interview 3 if it ran, + Interview 5 if it ran)
        # interviews_completed_this_month: Interview 1 (+ Interview 3 if it ran, + Interview 5 if it ran)
        # total_interviews = 4 or 5 (depends on Interview 3 and 5 creation)
        # abandoned_interviews = 1
        # average_time_per_interview_minutes: (30 + 60 (if Int3) + 45 (if Int5)) / (1 + (1 if Int3) + (1 if Int5))

        self.assertEqual(response.data['interviews_started_today'], 2)
        self.assertEqual(response.data['interviews_completed_today'], 1)
        
        # For weekly/monthly and average, need to be more dynamic based on actual data created
        completed_interviews_for_avg = Interview.objects.filter(status='Completed', abandoned=False, end_time__gt=F('start_time'))
        total_duration_seconds = sum([(i.end_time - i.start_time).total_seconds() for i in completed_interviews_for_avg])
        expected_avg_minutes = (total_duration_seconds / len(completed_interviews_for_avg) / 60) if completed_interviews_for_avg else 0
        
        self.assertAlmostEqual(response.data['average_time_per_interview_minutes'], expected_avg_minutes, places=2)

        total_interviews_count = Interview.objects.count()
        abandoned_count = Interview.objects.filter(abandoned=True).count()
        expected_abandonment_rate = (abandoned_count / total_interviews_count * 100) if total_interviews_count > 0 else 0
        self.assertAlmostEqual(response.data['interview_abandonment_rate'], expected_abandonment_rate, places=2)

        # More specific checks for weekly/monthly based on how many optional interviews were created
        # This part is tricky due to date logic in setUp, let's make it robust
        interviews_this_week_started = Interview.objects.filter(start_time__date__gte=self.start_of_week).count()
        interviews_this_week_completed = Interview.objects.filter(status='Completed', end_time__date__gte=self.start_of_week).count()
        interviews_this_month_started = Interview.objects.filter(start_time__date__gte=self.start_of_month).count()
        interviews_this_month_completed = Interview.objects.filter(status='Completed', end_time__date__gte=self.start_of_month).count()

        self.assertEqual(response.data['interviews_started_this_week'], interviews_this_week_started)
        self.assertEqual(response.data['interviews_completed_this_week'], interviews_this_week_completed)
        self.assertEqual(response.data['interviews_started_this_month'], interviews_this_month_started)
        self.assertEqual(response.data['interviews_completed_this_month'], interviews_this_month_completed)

    def test_engagement_metrics_no_interviews(self):
        Interview.objects.all().delete() # Clear all interviews
        response = self.client.get(self.engagement_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interviews_started_today'], 0)
        self.assertEqual(response.data['interviews_completed_today'], 0)
        self.assertEqual(response.data['interviews_started_this_week'], 0)
        self.assertEqual(response.data['interviews_completed_this_week'], 0)
        self.assertEqual(response.data['interviews_started_this_month'], 0)
        self.assertEqual(response.data['interviews_completed_this_month'], 0)
        self.assertEqual(response.data['average_time_per_interview_minutes'], 0)
        self.assertEqual(response.data['interview_abandonment_rate'], 0)


class CandidateProgressionAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Test Data for Candidate Progression
        # Create a second candidate for variety
        self.candidate2 = Candidate.objects.create(name='Test Candidate 2', email='candidate2@example.com', location='Test Location 2', current_stage='Invited')

        Interview.objects.create(
            status='Invited', start_time=self.middle_of_today, end_time=self.middle_of_today, employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )
        Interview.objects.create(
            status='Invited', start_time=self.middle_of_today, end_time=self.middle_of_today, employer=self.employer, candidate=self.candidate2, recruiter=self.recruiter
        )
        Interview.objects.create(
            status='Started', start_time=self.middle_of_today, end_time=self.middle_of_today, employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )
        Interview.objects.create(
            status='Completed', start_time=self.middle_of_today, end_time=self.middle_of_today, employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )
        Interview.objects.create(
            status='Shortlisted', start_time=self.middle_of_today, end_time=self.middle_of_today, employer=self.employer, candidate=self.candidate, recruiter=self.recruiter
        )
        # No 'Selected' interviews for this test case to check zero counts

        self.progression_url = reverse('candidate-progression')

    def test_get_candidate_progression_unauthenticated(self):
        self.client.credentials() # Clear authentication
        response = self.client.get(self.progression_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_candidate_progression_authenticated(self):
        response = self.client.get(self.progression_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Expected counts from setUp
        self.assertEqual(response.data['Invited']['count'], 2)
        self.assertEqual(response.data['Started']['count'], 1)
        self.assertEqual(response.data['Completed']['count'], 1)
        self.assertEqual(response.data['Shortlisted']['count'], 1)
        self.assertEqual(response.data['Selected']['count'], 0) # Explicitly check for 0

        # Expected display names
        self.assertEqual(response.data['Invited']['display_name'], 'Invited')
        self.assertEqual(response.data['Selected']['display_name'], 'Selected')
        
        # Test drop-off rates (assuming STATUS_CHOICES order is the funnel order)
        # Invited (2) -> Started (1) : ((2-1)/2)*100 = 50% drop-off from Invited to Started
        # Started (1) -> Completed (1) : ((1-1)/1)*100 = 0% drop-off
        # Completed (1) -> Shortlisted (1) : ((1-1)/1)*100 = 0% drop-off
        # Shortlisted (1) -> Selected (0) : ((1-0)/1)*100 = 100% drop-off
        
        self.assertEqual(response.data['Invited']['drop_off_from_previous_stage_percentage'], 0) # First stage
        self.assertAlmostEqual(response.data['Started']['drop_off_from_previous_stage_percentage'], 50.0, places=2)
        self.assertAlmostEqual(response.data['Completed']['drop_off_from_previous_stage_percentage'], 0.0, places=2)
        self.assertAlmostEqual(response.data['Shortlisted']['drop_off_from_previous_stage_percentage'], 0.0, places=2)
        self.assertAlmostEqual(response.data['Selected']['drop_off_from_previous_stage_percentage'], 100.0, places=2)

    def test_candidate_progression_no_interviews(self):
        Interview.objects.all().delete() # Clear all interviews
        response = self.client.get(self.progression_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for stage_key, stage_data in response.data.items():
            self.assertEqual(stage_data['count'], 0)
            self.assertEqual(stage_data['drop_off_from_previous_stage_percentage'], 0) # Or check if it's not present for first stage

# Basic Model Tests (if time permits, expand later)
class ModelCreationTests(APITestCase): # Can also use django.test.TestCase
    def test_create_employer(self):
        count_before = Employer.objects.count()
        Employer.objects.create(name="New Corp", industry="Tech")
        self.assertEqual(Employer.objects.count(), count_before + 1)

    def test_create_candidate(self):
        count_before = Candidate.objects.count()
        Candidate.objects.create(name="New Candidate", email="new@example.com", location="Remote", current_stage="Applied")
        self.assertEqual(Candidate.objects.count(), count_before + 1)

    def test_create_interview(self):
        user = User.objects.create_user(username='testmodeluser', password='password123')
        employer = Employer.objects.create(name="Model Employer")
        candidate = Candidate.objects.create(name="Model Candidate", email="model_cand@example.com")
        recruiter = Recruiter.objects.create(name="Model Recruiter", email="model_rec@example.com")
        
        count_before = Interview.objects.count()
        Interview.objects.create(
            status='Invited', 
            start_time=timezone.now(), 
            end_time=timezone.now() + timedelta(hours=1),
            employer=employer, 
            candidate=candidate, 
            recruiter=recruiter,
            questions_used="Q1,Q2"
        )
        self.assertEqual(Interview.objects.count(), count_before + 1)
