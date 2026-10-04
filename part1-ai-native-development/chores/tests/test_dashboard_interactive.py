import json
from datetime import date
from django.contrib.staticfiles import finders
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from chores.models import Assignment, Chore, Member


class DashboardInteractiveIntegrationTests(TestCase):
    """
    Test suite verifying TASK-10 requirements:
    - Static file serving for chores/dashboard.js
    - Template integration with script tags and DOM elements
    - Three status columns, badges, empty states, and allocator panel
    - Backing API workflows for mark-done and allocation
    """

    def setUp(self):
        self.client = Client()
        Assignment.objects.all().delete()
        Chore.objects.all().delete()
        Member.objects.all().delete()

        self.alice = Member.objects.create(name="Alice")
        self.bob = Member.objects.create(name="Bob")

        self.chore_dishes = Chore.objects.create(
            title="Wash Dishes",
            description="Clean and sanitize all dishes in sink.",
            frequency=Chore.Frequency.DAILY,
            effort_level=Chore.EffortLevel.LOW,
            is_active=True,
        )
        self.chore_vacuum = Chore.objects.create(
            title="Vacuum Common Areas",
            description="Vacuum hallway and living room carpets.",
            frequency=Chore.Frequency.WEEKLY,
            effort_level=Chore.EffortLevel.MEDIUM,
            is_active=True,
        )

    # --------------------------------------------------------------------------
    # 1. Static File Serving & Script Tag Tests
    # --------------------------------------------------------------------------

    def test_static_finder_locates_dashboard_js(self):
        """Staticfiles finder discovers chores/dashboard.js on the filesystem."""
        result = finders.find('chores/dashboard.js')
        self.assertIsNotNone(result, "Static finder could not locate chores/dashboard.js")
        self.assertTrue(result.endswith('dashboard.js'))

    def test_static_dashboard_js_served_via_http(self):
        """GET /static/chores/dashboard.js returns HTTP 200 with valid JavaScript."""
        response = self.client.get('/static/chores/dashboard.js')
        self.assertEqual(response.status_code, 200)

        # FileResponse streaming content
        if hasattr(response, 'streaming_content'):
            content = b''.join(response.streaming_content).decode('utf-8')
        else:
            content = response.content.decode('utf-8')

        self.assertIn("loadAssignments", content)
        self.assertIn("renderChoreBoard", content)
        self.assertIn("handleMarkDone", content)
        self.assertIn("handleAllocate", content)
        self.assertIn("updateBoardCounts", content)

    def test_dashboard_template_includes_script_tag(self):
        """GET / renders HTML with the deferred dashboard.js script tag."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('src="/static/chores/dashboard.js"', html)
        self.assertIn('defer', html)

    def test_dashboard_template_includes_csrf_meta_tag(self):
        """GET / includes meta tag with csrf-token for AJAX operations."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('<meta name="csrf-token"', html)

    # --------------------------------------------------------------------------
    # 2. DOM Elements for Chore Board Columns & Badges
    # --------------------------------------------------------------------------

    def test_dashboard_contains_three_status_columns_and_badges(self):
        """Dashboard HTML contains Pending, In Progress, and Completed columns and badge IDs."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        # Status columns
        self.assertIn('id="pending-column"', html)
        self.assertIn('id="in-progress-column"', html)
        self.assertIn('id="completed-column"', html)

        # Status column badge counters
        self.assertIn('id="pending-column-badge"', html)
        self.assertIn('id="in-progress-column-badge"', html)
        self.assertIn('id="completed-column-badge"', html)

    def test_dashboard_contains_initial_column_empty_states(self):
        """When no assignments exist, all three columns show fallback empty states."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn("No pending assignments", html)
        self.assertIn("No chores in progress", html)
        self.assertIn("No completed chores", html)

    def test_dashboard_contains_top_metric_counters(self):
        """Dashboard contains metric counter IDs for active chores, pending, completed, and members."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('id="metric-total-active-chores"', html)
        self.assertIn('id="metric-pending-assignments"', html)
        self.assertIn('id="metric-completed-this-week"', html)
        self.assertIn('id="metric-active-members"', html)

    # --------------------------------------------------------------------------
    # 3. DOM Elements for AI Allocator Panel
    # --------------------------------------------------------------------------

    def test_dashboard_contains_allocator_controls(self):
        """Dashboard HTML contains textarea notes, allocate button, spinner, and button text."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('id="allocator-notes"', html)
        self.assertIn('id="btn-allocate"', html)
        self.assertIn('id="allocator-spinner"', html)
        self.assertIn('id="btn-allocate-text"', html)
        self.assertIn("Run AI Allocation", html)

    def test_dashboard_contains_error_alert_box(self):
        """Dashboard contains hidden error alert box with default message."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('id="allocation-error"', html)
        self.assertIn('id="allocation-error-message"', html)
        self.assertIn("Failed to run allocation. Please try again.", html)

    def test_dashboard_contains_allocation_results_and_preview_containers(self):
        """Dashboard contains results summary, engine badge, and preview containers."""
        response = self.client.get(reverse('chores:dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        self.assertIn('id="allocation-results"', html)
        self.assertIn('id="allocator-engine-badge"', html)
        self.assertIn('id="allocation-summary"', html)
        self.assertIn('id="allocation-preview-container"', html)
        self.assertIn('id="allocation-preview-list"', html)

    # --------------------------------------------------------------------------
    # 4. Backing API Interactions (AJAX Endpoints invoked by dashboard.js)
    # --------------------------------------------------------------------------

    def test_api_assignments_get_returns_populated_columns_data(self):
        """GET /api/assignments/ returns all assignments with nested chore and member objects."""
        a1 = Assignment.objects.create(
            chore=self.chore_dishes,
            member=self.alice,
            status=Assignment.Status.PENDING,
            ai_reasoning="Alice has low effort history.",
        )
        a2 = Assignment.objects.create(
            chore=self.chore_vacuum,
            member=self.bob,
            status=Assignment.Status.COMPLETED,
            completed_at=timezone.now(),
        )

        response = self.client.get('/api/assignments/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

        # Check structured schema
        item = data[0]
        self.assertIn('id', item)
        self.assertIn('chore', item)
        self.assertIn('member', item)
        self.assertIn('status', item)
        self.assertIn('ai_reasoning', item)

    def test_mark_done_api_call_completes_assignment(self):
        """POST /api/assignments/<id>/complete/ marks assignment completed without page reload."""
        assignment = Assignment.objects.create(
            chore=self.chore_dishes,
            member=self.alice,
            status=Assignment.Status.PENDING,
        )

        url = f'/api/assignments/{assignment.id}/complete/'
        response = self.client.post(
            url,
            data=json.dumps({'status': 'completed'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'completed')
        self.assertIsNotNone(data['completed_at'])

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.COMPLETED)
        self.assertIsNotNone(assignment.completed_at)

    def test_allocate_api_call_empty_notes_round_robin(self):
        """POST /api/allocate/ with empty notes succeeds and generates assignments."""
        response = self.client.post(
            '/api/allocate/',
            data=json.dumps({'user_notes': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('engine_used', data)
        self.assertIn('raw_reasoning_summary', data)
        self.assertGreater(len(data['assignments']), 0)

        # Assignments should be persisted in DB
        self.assertEqual(Assignment.objects.filter(status=Assignment.Status.PENDING).count(), 2)

    def test_allocate_api_call_with_notes(self):
        """POST /api/allocate/ with custom notes receives and records reasoning."""
        notes = "Alice is busy with exams this week; Bob handles vacuuming."
        response = self.client.post(
            '/api/allocate/',
            data=json.dumps({'user_notes': notes}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('raw_reasoning_summary', data)
        self.assertGreater(len(data['assignments']), 0)

    def test_allocate_api_call_error_when_no_members_or_chores(self):
        """POST /api/allocate/ returns 400 error alert payload if no active members exist."""
        Member.objects.all().delete()
        response = self.client.post(
            '/api/allocate/',
            data=json.dumps({'user_notes': 'Test notes'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
