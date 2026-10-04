from datetime import timedelta
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chores.models import Assignment, Chore, Member


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Clean up database state for isolated tests
        Assignment.objects.all().delete()
        Chore.objects.all().delete()
        Member.objects.all().delete()

    def test_dashboard_url_resolves_and_returns_200(self):
        """GET / and GET reverse('chores:dashboard') return HTTP 200 OK."""
        response_root = self.client.get('/')
        self.assertEqual(response_root.status_code, 200)

        response_named = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response_named.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        """GET / renders chores/dashboard.html template."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chores/dashboard.html')

    def test_dashboard_header_and_status_pill(self):
        """Dashboard renders expected header title and status pill."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("AI Household Chore Manager", content)
        self.assertIn("Household Active", content)

    def test_dashboard_metrics_bar_cards_present(self):
        """Dashboard renders 4 top metric cards with expected headings."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Total Active Chores", content)
        self.assertIn("Pending Assignments", content)
        self.assertIn("Completed This Week", content)
        self.assertIn("Active Household Members", content)

    def test_dashboard_main_container_element_ids(self):
        """Dashboard contains #chore-board-container and #ai-allocator-container."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="chore-board-container"', content)
        self.assertIn('id="ai-allocator-container"', content)

    def test_dashboard_allocator_and_board_sub_elements(self):
        """Dashboard contains allocator input, button, results, and board status columns."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="allocator-notes"', content)
        self.assertIn('id="btn-allocate"', content)
        self.assertIn('id="allocation-results"', content)
        self.assertIn('id="pending-column"', content)
        self.assertIn('id="in-progress-column"', content)
        self.assertIn('id="completed-column"', content)

    def test_dashboard_styling_assets_included(self):
        """Dashboard includes Tailwind CSS CDN link and Inter Google Font."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("cdn.tailwindcss.com", content)
        self.assertIn("fonts.googleapis.com", content)
        self.assertIn("Inter", content)

    def test_dashboard_responsive_grid_layout(self):
        """Dashboard includes responsive grid classes for desktop 2-col / mobile 1-col."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("lg:grid-cols-3", content)
        self.assertIn("lg:col-span-2", content)
        self.assertIn("lg:col-span-1", content)

    def test_dashboard_empty_state_metrics_and_fallbacks(self):
        """When DB is empty, metrics context defaults to 0 and empty state text displays."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_active_chores'], 0)
        self.assertEqual(response.context['pending_assignments_count'], 0)
        self.assertEqual(response.context['completed_this_week_count'], 0)
        self.assertEqual(response.context['active_members_count'], 0)

        content = response.content.decode('utf-8')
        self.assertIn("No active chores", content)
        self.assertIn("No pending assignments", content)
        self.assertIn("No completed chores this week", content)
        self.assertIn("No active members", content)

    def test_dashboard_metrics_with_populated_data(self):
        """Context accurately reflects counts for chores, pending assignments, completed, and members."""
        m1 = Member.objects.create(name="Alice")
        m2 = Member.objects.create(name="Bob")

        # 2 active chores, 1 inactive chore
        c1 = Chore.objects.create(title="Vacuum Living Room", is_active=True)
        c2 = Chore.objects.create(title="Clean Kitchen", is_active=True)
        c3 = Chore.objects.create(title="Mow Lawn", is_active=False)

        now = timezone.now()
        # 2 pending assignments
        Assignment.objects.create(chore=c1, member=m1, status=Assignment.Status.PENDING)
        Assignment.objects.create(chore=c2, member=m2, status=Assignment.Status.PENDING)

        # 1 completed this week (completed_at set to now)
        Assignment.objects.create(
            chore=c1, member=m2,
            status=Assignment.Status.COMPLETED,
            completed_at=now,
        )

        # 1 completed this week (completed_at is None, assigned_date is today)
        Assignment.objects.create(
            chore=c2, member=m1,
            status=Assignment.Status.COMPLETED,
            completed_at=None,
            assigned_date=now.date(),
        )

        # 1 completed outside this week (14 days ago)
        Assignment.objects.create(
            chore=c1, member=m1,
            status=Assignment.Status.COMPLETED,
            completed_at=now - timedelta(days=14),
            assigned_date=(now - timedelta(days=14)).date(),
        )

        # 1 skipped assignment
        Assignment.objects.create(
            chore=c2, member=m2,
            status=Assignment.Status.SKIPPED,
        )

        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['total_active_chores'], 2)
        self.assertEqual(response.context['pending_assignments_count'], 2)
        self.assertEqual(response.context['completed_this_week_count'], 2)
        self.assertEqual(response.context['active_members_count'], 2)

        content = response.content.decode('utf-8')
        # Check rendered numbers in HTML
        self.assertIn('id="metric-total-active-chores"', content)
        self.assertIn('id="metric-pending-assignments"', content)
        self.assertIn('id="metric-completed-this-week"', content)
        self.assertIn('id="metric-active-members"', content)
