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
