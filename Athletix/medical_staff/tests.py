from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from player.models import Sport
from user.models import MedicalProfile

from .models import AthleteHealthRecord, MedicalFeedback


User = get_user_model()


class MedicalStaffDashboardTests(TestCase):
    def setUp(self):
        self.medical_user = User.objects.create_user(
            email='medic@test.com',
            name='Medical User',
            password='pass12345',
            role='medical',
        )
        MedicalProfile.objects.create(user=self.medical_user, specialty='Sports Medicine')
        self.athlete = User.objects.create_user(
            email='athlete_medical@test.com',
            name='Athlete Medical',
            password='pass12345',
            role='athlete',
        )
        self.other_medical_user = User.objects.create_user(
            email='other_medic@test.com',
            name='Other Medical User',
            password='pass12345',
            role='medical',
        )
        MedicalProfile.objects.create(user=self.other_medical_user, specialty='Physio')
        Sport.objects.get_or_create(name='Medical Test Sport')

    def test_medical_dashboard_accessible_for_medical_user(self):
        self.client.force_login(self.medical_user)
        response = self.client.get(reverse('medical_staff:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Staff Dashboard')

    def test_add_feedback_creates_feedback_for_athlete(self):
        AthleteHealthRecord.objects.create(
            athlete=self.athlete,
            medical_staff=self.medical_user,
            heart_rate=66,
            fatigue_level=2,
        )
        self.client.force_login(self.medical_user)
        response = self.client.post(
            reverse('medical_staff:add_feedback'),
            data={
                'athlete': self.athlete.id,
                'feedback_type': 'health',
                'title': 'General Health Follow-up',
                'feedback': 'Keep hydration and active recovery.',
                'recommendations': 'Sleep 8 hours daily.',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('medical_staff:dashboard'))
        self.assertTrue(
            MedicalFeedback.objects.filter(
                athlete=self.athlete, medical_staff=self.medical_user
            ).exists()
        )

    def test_add_feedback_for_record_creates_feedback_and_sets_reviewer(self):
        record = AthleteHealthRecord.objects.create(
            athlete=self.athlete,
            medical_staff=self.medical_user,
            heart_rate=68,
            blood_pressure='120/80',
            weight_kg='65.50',
            sleep_hours='7.5',
            fatigue_level=3,
            injury_status='minor',
            injury_notes='Mild knee pain',
            recovery_status='watch',
            performance_notes='Needs reduced load for 3 days',
        )

        self.client.force_login(self.medical_user)
        response = self.client.post(
            reverse('medical_staff:add_feedback_for_record', args=[record.id]),
            data={
                'feedback_type': 'health',
                'title': 'Recovery Monitoring',
                'feedback': 'Continue light recovery sessions.',
                'recommendations': 'Sleep 8 hours daily.',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('medical_staff:dashboard'))
        self.assertTrue(
            MedicalFeedback.objects.filter(
                athlete=self.athlete, medical_staff=self.medical_user
            ).exists()
        )
        record.refresh_from_db()
        self.assertEqual(record.medical_staff, self.medical_user)

    def test_dashboard_shows_only_assigned_athletes(self):
        AthleteHealthRecord.objects.create(
            athlete=self.athlete,
            medical_staff=self.medical_user,
            heart_rate=65,
            fatigue_level=2,
        )
        other_athlete = User.objects.create_user(
            email='other_athlete@test.com',
            name='Other Athlete',
            password='pass12345',
            role='athlete',
        )
        AthleteHealthRecord.objects.create(
            athlete=other_athlete,
            medical_staff=self.other_medical_user,
            heart_rate=72,
            fatigue_level=4,
        )

        self.client.force_login(self.medical_user)
        response = self.client.get(reverse('medical_staff:dashboard'))
        self.assertContains(response, 'Athlete Medical')
        self.assertNotContains(response, 'Other Athlete')
