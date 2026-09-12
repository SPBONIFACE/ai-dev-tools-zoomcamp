import hashlib
import os
import sqlite3
from django.conf import settings
from django.test import TestCase
from django.db import connection

from chores.models import Assignment, Chore, Member


class DatabaseIsolationTests(TestCase):
    """
    Tests ensuring strict database isolation during automated test execution.
    Verifies that the root db.sqlite3 file is never written to, polluted, or
    corrupted by test runs.
    """

    def test_runner_uses_isolated_test_database(self):
        """Verify Django test runner operates on an isolated test database."""
        current_db_name = str(connection.settings_dict['NAME']).lower()
        # Django prefixes test databases with 'test_' or uses in-memory databases ('memorydb')
        self.assertTrue(
            current_db_name.startswith('test_')
            or 'test' in current_db_name
            or 'memory' in current_db_name
            or current_db_name == ':memory:',
            f"Active test database name '{current_db_name}' should be isolated from production.",
        )

    def test_root_database_remains_unpolluted_by_test_records(self):
        """
        Verify that creating, updating, and deleting records in the test runner
        leaves the root db.sqlite3 file completely unmodified and unpolluted.
        """
        root_db_path = settings.BASE_DIR / 'db.sqlite3'
        if not root_db_path.exists():
            self.skipTest("Root db.sqlite3 does not exist.")

        # Compute initial hash of root database
        with open(root_db_path, 'rb') as f:
            initial_hash = hashlib.sha256(f.read()).hexdigest()

        # Generate unique canary identifiers for this test execution
        canary_member_name = "__CANARY_ISOLATION_TEST_MEMBER__"
        canary_chore_title = "__CANARY_ISOLATION_TEST_CHORE__"

        # Perform mutations inside test environment
        member = Member.objects.create(name=canary_member_name)
        chore = Chore.objects.create(title=canary_chore_title)
        Assignment.objects.create(
            chore=chore,
            member=member,
            ai_reasoning="Isolation test canary.",
        )

        # Verify records exist in test connection
        self.assertTrue(Member.objects.filter(name=canary_member_name).exists())
        self.assertTrue(Chore.objects.filter(title=canary_chore_title).exists())

        # Inspect root db.sqlite3 directly via independent sqlite connection
        conn = sqlite3.connect(root_db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM chores_member WHERE name = ?", (canary_member_name,))
            count_member = cursor.fetchone()[0]
            self.assertEqual(
                count_member, 0,
                "Root database was polluted with test Member record!",
            )

            cursor.execute("SELECT COUNT(*) FROM chores_chore WHERE title = ?", (canary_chore_title,))
            count_chore = cursor.fetchone()[0]
            self.assertEqual(
                count_chore, 0,
                "Root database was polluted with test Chore record!",
            )
        finally:
            conn.close()

        # Verify root database file content was not modified
        with open(root_db_path, 'rb') as f:
            post_hash = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(
            initial_hash,
            post_hash,
            "Root db.sqlite3 file content was altered during test execution!",
        )


class CIWorkflowTests(TestCase):
    """
    Test suite validating GitHub Actions CI workflow (.github/workflows/ci.yml).
    Verifies workflow file existence, YAML syntax compliance, event triggers,
    environment variables, action dependencies, and execution steps.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.workflow_path = settings.BASE_DIR / '.github' / 'workflows' / 'ci.yml'
        cls.content = cls.workflow_path.read_text(encoding='utf-8') if cls.workflow_path.exists() else ''

    def test_workflow_file_exists(self):
        """Verify .github/workflows/ci.yml exists and is not empty."""
        self.assertTrue(self.workflow_path.exists(), "Workflow file .github/workflows/ci.yml does not exist.")
        self.assertGreater(len(self.content.strip()), 0, "Workflow file is empty.")

    def test_workflow_yaml_syntax_and_formatting(self):
        """Verify YAML syntax formatting: no illegal tabs, valid top-level keys."""
        self.assertNotIn('\t', self.content, "YAML workflow must use spaces instead of tab indentation.")

        for key in ['name:', 'on:', 'env:', 'jobs:']:
            self.assertIn(key, self.content, f"Missing required top-level YAML key: {key}")

        lines = self.content.splitlines()
        for i, line in enumerate(lines, start=1):
            if not line.strip() or line.strip().startswith('#'):
                continue
            indent = len(line) - len(line.lstrip(' '))
            self.assertEqual(
                indent % 2, 0,
                f"Line {i} has irregular indentation of {indent} spaces (must be multiple of 2): '{line}'",
            )

    def test_workflow_name_and_triggers(self):
        """Verify workflow name is 'CI Pipeline' and triggers on push and PR to main."""
        self.assertIn("name: CI Pipeline", self.content)
        self.assertIn("push:", self.content)
        self.assertIn("pull_request:", self.content)
        self.assertIn("branches: [ main ]", self.content)

    def test_workflow_environment_variables(self):
        """Verify environment variables AI_PROVIDER=mock and PYTHONUNBUFFERED=1."""
        self.assertIn("AI_PROVIDER: mock", self.content)
        self.assertIn('PYTHONUNBUFFERED: "1"', self.content)

    def test_workflow_job_runner(self):
        """Verify job test-and-build runs on ubuntu-latest."""
        self.assertIn("test-and-build:", self.content)
        self.assertIn("runs-on: ubuntu-latest", self.content)

    def test_workflow_action_versions(self):
        """Verify standard GitHub actions with correct versions are used."""
        self.assertIn("actions/checkout@v4", self.content)
        self.assertIn("astral-sh/setup-uv@v5", self.content)
        self.assertIn("actions/setup-python@v5", self.content)
        self.assertIn('python-version: "3.11"', self.content)
        self.assertIn("enable-cache: true", self.content)

    def test_workflow_execution_steps(self):
        """Verify required dependency sync, linting, testing, and Docker build steps."""
        self.assertIn("uv sync --frozen", self.content)
        self.assertIn("ruff check .", self.content)
        self.assertIn("uv run python manage.py test", self.content)
        self.assertIn("docker build -t chore-manager:ci .", self.content)

