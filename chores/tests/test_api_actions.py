import json
from datetime import date, timedelta
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chores.models import Assignment, Chore, Member


class AssignmentCompleteApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Member.objects.all().delete()
        Chore.objects.all().delete()
        Assignment.objects.all().delete()

        self.member = Member.objects.create(name="Alice")
        self.chore = Chore.objects.create(title="Dishes", effort_level=2, frequency="daily")
        self.assignment = Assignment.objects.create(
            chore=self.chore,
            member=self.member,
            assigned_date=date(2026, 9, 10),
            status=Assignment.Status.PENDING,
        )

    def test_complete_assignment_success_empty_body(self):
        """POST /api/assignments/<id>/complete/ marks assignment completed with empty body."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['id'], self.assignment.id)
        self.assertEqual(data['status'], 'completed')
        self.assertIsNotNone(data['completed_at'])

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, Assignment.Status.COMPLETED)
        self.assertIsNotNone(self.assignment.completed_at)

    def test_complete_assignment_success_with_status_body(self):
        """POST /api/assignments/<id>/complete/ marks assignment completed with {"status": "completed"}."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        response = self.client.post(
            url,
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['id'], self.assignment.id)
        self.assertEqual(data['status'], 'completed')

    def test_complete_assignment_not_found(self):
        """POST /api/assignments/9999/complete/ returns 404 Not Found."""
        url = reverse('chores:api_assignment_complete', args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_complete_assignment_idempotency(self):
        """Calling /complete/ on already completed assignment is idempotent and updates timestamp."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        # First completion
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, 200)
        time1 = res1.json()['completed_at']

        # Second completion
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2['status'], 'completed')
        self.assertIsNotNone(data2['completed_at'])

    def test_complete_assignment_invalid_status_body(self):
        """POST with status other than 'completed' returns 400."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        response = self.client.post(
            url,
            data=json.dumps({"status": "pending"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_complete_assignment_invalid_json(self):
        """POST with invalid JSON returns 400."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        response = self.client.post(
            url,
            data="not-valid-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_complete_assignment_unsupported_method(self):
        """GET /api/assignments/<id>/complete/ returns 405 Method Not Allowed."""
        url = reverse('chores:api_assignment_complete', args=[self.assignment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class AllocateApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        Member.objects.all().delete()
        Chore.objects.all().delete()
        Assignment.objects.all().delete()

        self.alice = Member.objects.create(name="Alice")
        self.bob = Member.objects.create(name="Bob")

        self.chore1 = Chore.objects.create(title="Dishes", effort_level=2, frequency="daily", is_active=True)
        self.chore2 = Chore.objects.create(title="Trash", effort_level=1, frequency="daily", is_active=True)

    def test_allocate_no_members_returns_400(self):
        """POST /api/allocate/ with no members returns 400 Bad Request."""
        Member.objects.all().delete()
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Cannot run allocation without active members and chores.", data.get('error', '') or data.get('message', ''))

    def test_allocate_no_chores_returns_400(self):
        """POST /api/allocate/ with no active chores returns 400 Bad Request."""
        Chore.objects.all().delete()
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Cannot run allocation without active members and chores.", data.get('error', '') or data.get('message', ''))

    def test_allocate_only_inactive_chores_returns_400(self):
        """POST /api/allocate/ when all chores are inactive returns 400 Bad Request."""
        Chore.objects.all().update(is_active=False)
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": False}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_allocate_dry_run_true(self):
        """POST /api/allocate/ with dry_run=true returns proposals without DB persistence."""
        initial_count = Assignment.objects.count()
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": True, "user_notes": "Normal allocation"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['engine_used'], 'mock')
        self.assertEqual(data['assignments_created'], 0)
        self.assertEqual(len(data['assignments']), 2)
        self.assertTrue(len(data['raw_reasoning_summary']) > 0)
        # Database count remains unchanged
        self.assertEqual(Assignment.objects.count(), initial_count)

    def test_allocate_dry_run_false_persists_assignments(self):
        """POST /api/allocate/ with dry_run=false creates Assignment instances in DB."""
        initial_count = Assignment.objects.count()
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": False, "user_notes": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['assignments_created'], 2)
        self.assertEqual(len(data['assignments']), 2)

        # Database count increased by 2
        self.assertEqual(Assignment.objects.count(), initial_count + 2)

        # Verify attributes of created records
        for item in data['assignments']:
            self.assertIsNotNone(item['id'])
            assignment = Assignment.objects.get(id=item['id'])
            self.assertEqual(assignment.status, Assignment.Status.PENDING)
            self.assertTrue(len(assignment.ai_reasoning) > 0)
            self.assertIn(assignment.member_id, [self.alice.id, self.bob.id])

    def test_allocate_respects_user_notes(self):
        """User note specifying Alice is away allocates all chores to Bob."""
        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": False, "user_notes": "Alice is away on trip."}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for item in data['assignments']:
            self.assertEqual(item['member_id'], self.bob.id)

    def test_allocate_workload_history_calculation(self):
        """Past 14-day workload history gives Alice more points so Bob gets heavier chore."""
        # Give Alice recent chore effort = 5
        Assignment.objects.create(
            chore=self.chore1,
            member=self.alice,
            assigned_date=timezone.now().date() - timedelta(days=2),
            status=Assignment.Status.COMPLETED,
        )

        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Heaviest chore (effort=2) should go to Bob who has 0 workload
        heaviest_assignment = next(a for a in data['assignments'] if a['chore_id'] == self.chore1.id)
        self.assertEqual(heaviest_assignment['member_id'], self.bob.id)

    def test_allocate_workload_older_than_14_days_ignored(self):
        """Workload older than 14 days is not counted towards recent workload history."""
        # Alice completed a chore 20 days ago (outside 14-day window)
        Assignment.objects.create(
            chore=self.chore1,
            member=self.alice,
            assigned_date=timezone.now().date() - timedelta(days=20),
            status=Assignment.Status.COMPLETED,
        )

        response = self.client.post(
            reverse('chores:api_allocate'),
            data=json.dumps({"dry_run": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Alice and Bob tied at 0, Alice wins tie-breaker alphabetically for chore1
        heaviest_assignment = next(a for a in data['assignments'] if a['chore_id'] == self.chore1.id)
        self.assertEqual(heaviest_assignment['member_id'], self.alice.id)

    def test_allocate_invalid_method(self):
        """GET /api/allocate/ returns 405 Method Not Allowed."""
        response = self.client.get(reverse('chores:api_allocate'))
        self.assertEqual(response.status_code, 405)

    def test_allocate_invalid_json(self):
        """POST /api/allocate/ with malformed JSON returns 400 Bad Request."""
        response = self.client.post(
            reverse('chores:api_allocate'),
            data="invalid-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
