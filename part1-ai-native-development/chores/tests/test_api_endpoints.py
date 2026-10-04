import json
from datetime import date
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chores.models import Assignment, Chore, Member


class MemberEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_members_empty(self):
        """GET /api/members/ returns 200 with empty list when no members exist."""
        Member.objects.all().delete()
        response = self.client.get(reverse('chores:api_members'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_members_with_stats(self):
        """GET /api/members/ returns members with correct pending and completed counts."""
        Member.objects.all().delete()
        Chore.objects.all().delete()

        m1 = Member.objects.create(name="Alice")
        m2 = Member.objects.create(name="Bob")
        c1 = Chore.objects.create(title="Dishes")
        c2 = Chore.objects.create(title="Trash")

        # Alice: 2 pending, 1 completed
        Assignment.objects.create(chore=c1, member=m1, status=Assignment.Status.PENDING)
        Assignment.objects.create(chore=c2, member=m1, status=Assignment.Status.PENDING)
        Assignment.objects.create(chore=c1, member=m1, status=Assignment.Status.COMPLETED)

        # Bob: 0 pending, 1 completed
        Assignment.objects.create(chore=c2, member=m2, status=Assignment.Status.COMPLETED)

        response = self.client.get(reverse('chores:api_members'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

        alice_data = next(m for m in data if m['id'] == m1.id)
        self.assertEqual(alice_data['name'], 'Alice')
        self.assertIn('created_at', alice_data)
        self.assertEqual(alice_data['pending_assignments_count'], 2)
        self.assertEqual(alice_data['completed_assignments_count'], 1)

        bob_data = next(m for m in data if m['id'] == m2.id)
        self.assertEqual(bob_data['name'], 'Bob')
        self.assertEqual(bob_data['pending_assignments_count'], 0)
        self.assertEqual(bob_data['completed_assignments_count'], 1)

    def test_post_member_success(self):
        """POST /api/members/ creates a new member and returns 201."""
        response = self.client.post(
            reverse('chores:api_members'),
            data=json.dumps({"name": "David"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'David')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertEqual(data['pending_assignments_count'], 0)
        self.assertEqual(data['completed_assignments_count'], 0)
        self.assertTrue(Member.objects.filter(name='David').exists())

    def test_post_member_duplicate_name(self):
        """POST /api/members/ returns 400 when member name already exists."""
        Member.objects.create(name="David")
        response = self.client.post(
            reverse('chores:api_members'),
            data=json.dumps({"name": "David"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Member with this name already exists."})

    def test_post_member_missing_name(self):
        """POST /api/members/ returns 400 when name is missing or empty."""
        response = self.client.post(
            reverse('chores:api_members'),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

        response_empty = self.client.post(
            reverse('chores:api_members'),
            data=json.dumps({"name": "   "}),
            content_type="application/json",
        )
        self.assertEqual(response_empty.status_code, 400)
        self.assertIn("error", response_empty.json())

    def test_member_unsupported_method(self):
        """DELETE /api/members/ returns 405 Method Not Allowed."""
        response = self.client.delete(reverse('chores:api_members'))
        self.assertEqual(response.status_code, 405)


class ChoreEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_chores_empty(self):
        """GET /api/chores/ returns 200 with empty list when no chores exist."""
        Chore.objects.all().delete()
        response = self.client.get(reverse('chores:api_chores'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_chores_default_active(self):
        """GET /api/chores/ defaults to returning only active chores."""
        Chore.objects.all().delete()
        c1 = Chore.objects.create(title="Active Chore", is_active=True)
        c2 = Chore.objects.create(title="Archived Chore", is_active=False)

        response = self.client.get(reverse('chores:api_chores'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], c1.id)
        self.assertEqual(data[0]['title'], 'Active Chore')
        self.assertTrue(data[0]['is_active'])

    def test_get_chores_filter_inactive(self):
        """GET /api/chores/?is_active=false returns inactive chores."""
        Chore.objects.all().delete()
        Chore.objects.create(title="Active Chore", is_active=True)
        c2 = Chore.objects.create(title="Archived Chore", is_active=False)

        response = self.client.get(reverse('chores:api_chores') + '?is_active=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], c2.id)
        self.assertFalse(data[0]['is_active'])

    def test_get_chores_filter_all(self):
        """GET /api/chores/?is_active=all returns both active and inactive chores."""
        Chore.objects.all().delete()
        Chore.objects.create(title="Active Chore", is_active=True)
        Chore.objects.create(title="Archived Chore", is_active=False)

        response = self.client.get(reverse('chores:api_chores') + '?is_active=all')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_chores_invalid_filter(self):
        """GET /api/chores/?is_active=maybe returns 400."""
        response = self.client.get(reverse('chores:api_chores') + '?is_active=maybe')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_post_chore_success(self):
        """POST /api/chores/ creates chore definition and returns 201."""
        payload = {
            "title": "Mop Floor",
            "description": "Kitchen and hall",
            "effort_level": 2,
            "frequency": "weekly",
            "is_active": True,
        }
        response = self.client.post(
            reverse('chores:api_chores'),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], "Mop Floor")
        self.assertEqual(data['effort_level'], 2)
        self.assertEqual(data['frequency'], "weekly")
        self.assertEqual(data['description'], "Kitchen and hall")
        self.assertTrue(data['is_active'])
        self.assertIn('id', data)

    def test_post_chore_missing_title(self):
        """POST /api/chores/ returns 400 when title is missing."""
        payload = {"effort_level": 2, "frequency": "weekly"}
        response = self.client.post(
            reverse('chores:api_chores'),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_post_chore_invalid_effort_level(self):
        """POST /api/chores/ returns 400 when effort_level is not 1, 2, or 3."""
        for invalid_effort in [0, 4, -1, "high"]:
            payload = {"title": "Test", "effort_level": invalid_effort}
            response = self.client.post(
                reverse('chores:api_chores'),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json())

    def test_post_chore_invalid_frequency(self):
        """POST /api/chores/ returns 400 when frequency is invalid."""
        payload = {"title": "Test", "frequency": "monthly_never"}
        response = self.client.post(
            reverse('chores:api_chores'),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())


class AssignmentEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()
        Member.objects.all().delete()
        Chore.objects.all().delete()

        self.member1 = Member.objects.create(name="Alice")
        self.member2 = Member.objects.create(name="Bob")
        self.chore1 = Chore.objects.create(title="Wash Dishes", effort_level=1, frequency="daily")
        self.chore2 = Chore.objects.create(title="Vacuum Rugs", effort_level=2, frequency="weekly")

        self.assignment1 = Assignment.objects.create(
            chore=self.chore1,
            member=self.member1,
            assigned_date=date(2026, 9, 10),
            due_date=date(2026, 9, 11),
            status=Assignment.Status.PENDING,
            ai_reasoning="Alice has lowest daily workload.",
        )
        self.assignment2 = Assignment.objects.create(
            chore=self.chore2,
            member=self.member2,
            assigned_date=date(2026, 9, 9),
            due_date=date(2026, 9, 12),
            status=Assignment.Status.COMPLETED,
            completed_at=timezone.now(),
            ai_reasoning="Bob completed last week.",
        )

    def test_get_assignments_all(self):
        """GET /api/assignments/ returns list of all assignments with nested structures."""
        response = self.client.get(reverse('chores:api_assignments'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

        item = next(a for a in data if a['id'] == self.assignment1.id)
        self.assertEqual(item['status'], 'pending')
        self.assertEqual(item['assigned_date'], '2026-09-10')
        self.assertEqual(item['due_date'], '2026-09-11')
        self.assertIsNone(item['completed_at'])
        self.assertEqual(item['ai_reasoning'], "Alice has lowest daily workload.")

        # Nested chore summary
        self.assertEqual(item['chore']['id'], self.chore1.id)
        self.assertEqual(item['chore']['title'], 'Wash Dishes')
        self.assertEqual(item['chore']['effort_level'], 1)
        self.assertEqual(item['chore']['frequency'], 'daily')

        # Nested member summary
        self.assertEqual(item['member']['id'], self.member1.id)
        self.assertEqual(item['member']['name'], 'Alice')

    def test_get_assignments_filter_by_status(self):
        """GET /api/assignments/?status=pending filters by status."""
        response = self.client.get(reverse('chores:api_assignments') + '?status=pending')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.assignment1.id)

        response_completed = self.client.get(reverse('chores:api_assignments') + '?status=completed')
        self.assertEqual(response_completed.status_code, 200)
        data_completed = response_completed.json()
        self.assertEqual(len(data_completed), 1)
        self.assertEqual(data_completed[0]['id'], self.assignment2.id)

    def test_get_assignments_filter_by_member_id(self):
        """GET /api/assignments/?member_id=<id> filters by member."""
        response = self.client.get(f"{reverse('chores:api_assignments')}?member_id={self.member2.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.assignment2.id)

    def test_get_assignments_filter_invalid_status(self):
        """GET /api/assignments/?status=invalid returns 400."""
        response = self.client.get(reverse('chores:api_assignments') + '?status=invalid_status')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_get_assignments_filter_invalid_member_id(self):
        """GET /api/assignments/?member_id=abc returns 400."""
        response = self.client.get(reverse('chores:api_assignments') + '?member_id=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_assignments_unsupported_methods(self):
        """POST, PUT, and DELETE on /api/assignments/ return 405 Method Not Allowed."""
        url = reverse('chores:api_assignments')
        for method in ['post', 'put', 'delete', 'patch']:
            client_method = getattr(self.client, method)
            response = client_method(url, data={}, content_type="application/json")
            self.assertEqual(
                response.status_code,
                405,
                f"Expected HTTP 405 for {method.upper()} on assignments endpoint, got {response.status_code}",
            )


class ResourceEndpointMethodNotAllowedTests(TestCase):
    """Tests verifying HTTP 405 on invalid HTTP verbs across resource endpoints."""

    def setUp(self):
        self.client = Client()

    def test_members_unsupported_methods(self):
        """PUT, DELETE, and PATCH on /api/members/ return 405 Method Not Allowed."""
        url = reverse('chores:api_members')
        for method in ['put', 'delete', 'patch']:
            client_method = getattr(self.client, method)
            response = client_method(url, data={}, content_type="application/json")
            self.assertEqual(
                response.status_code,
                405,
                f"Expected HTTP 405 for {method.upper()} on members endpoint, got {response.status_code}",
            )

    def test_chores_unsupported_methods(self):
        """PUT, DELETE, and PATCH on /api/chores/ return 405 Method Not Allowed."""
        url = reverse('chores:api_chores')
        for method in ['put', 'delete', 'patch']:
            client_method = getattr(self.client, method)
            response = client_method(url, data={}, content_type="application/json")
            self.assertEqual(
                response.status_code,
                405,
                f"Expected HTTP 405 for {method.upper()} on chores endpoint, got {response.status_code}",
            )

