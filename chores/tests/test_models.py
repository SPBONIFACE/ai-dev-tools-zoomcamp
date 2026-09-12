from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.contrib import admin
from django.core.management import call_command
from chores.models import Member, Chore, Assignment
from chores.admin import MemberAdmin, ChoreAdmin, AssignmentAdmin


class MemberModelTests(TestCase):
    """Tests covering the Member model."""

    def test_create_member(self):
        member = Member.objects.create(name='Alice')
        self.assertEqual(member.name, 'Alice')
        self.assertIsNotNone(member.created_at)

    def test_member_str_representation(self):
        member = Member.objects.create(name='Bob')
        self.assertEqual(str(member), 'Bob')

    def test_member_unique_name_constraint(self):
        Member.objects.create(name='Charlie')
        with self.assertRaises(IntegrityError):
            Member.objects.create(name='Charlie')

    def test_member_ordering(self):
        Member.objects.create(name='Zara')
        Member.objects.create(name='Alex')
        members = list(Member.objects.all().values_list('name', flat=True))
        self.assertEqual(members, ['Alex', 'Zara'])


class ChoreModelTests(TestCase):
    """Tests covering the Chore model."""

    def test_chore_defaults(self):
        chore = Chore.objects.create(title='Wipe Tables')
        self.assertTrue(chore.is_active)
        self.assertEqual(chore.frequency, Chore.Frequency.WEEKLY)
        self.assertEqual(chore.effort_level, Chore.EffortLevel.MEDIUM)
        self.assertEqual(chore.description, '')

    def test_chore_str_representation(self):
        chore = Chore.objects.create(
            title='Clean Kitchen',
            frequency=Chore.Frequency.DAILY,
        )
        self.assertEqual(str(chore), 'Clean Kitchen (Daily)')

    def test_chore_different_effort_levels_and_frequencies(self):
        chore_easy = Chore.objects.create(
            title='Take Out Trash',
            frequency=Chore.Frequency.DAILY,
            effort_level=Chore.EffortLevel.LOW,
        )
        chore_heavy = Chore.objects.create(
            title='Scrub Oven',
            frequency=Chore.Frequency.BIWEEKLY,
            effort_level=Chore.EffortLevel.HIGH,
        )
        self.assertEqual(chore_easy.effort_level, 1)
        self.assertEqual(chore_heavy.effort_level, 3)


class AssignmentModelTests(TestCase):
    """Tests covering Assignment relations and state transitions."""

    def setUp(self):
        self.member = Member.objects.create(name='Alice')
        self.chore = Chore.objects.create(
            title='Clean Kitchen',
            frequency=Chore.Frequency.DAILY,
        )

    def test_create_assignment_default_status(self):
        assignment = Assignment.objects.create(
            chore=self.chore,
            member=self.member,
            due_date=timezone.now().date(),
        )
        self.assertEqual(assignment.status, Assignment.Status.PENDING)
        self.assertIsNone(assignment.completed_at)
        self.assertIn('Clean Kitchen -> Alice (Pending)', str(assignment))

    def test_mark_completed_workflow(self):
        assignment = Assignment.objects.create(
            chore=self.chore,
            member=self.member,
            due_date=timezone.now().date(),
            ai_reasoning='Alice offered to clean Monday.',
        )
        self.assertIsNone(assignment.completed_at)

        assignment.mark_completed()
        assignment.refresh_from_db()

        self.assertEqual(assignment.status, Assignment.Status.COMPLETED)
        self.assertIsNotNone(assignment.completed_at)
        self.assertEqual(assignment.ai_reasoning, 'Alice offered to clean Monday.')

    def test_cascade_deletion_on_member_delete(self):
        Assignment.objects.create(
            chore=self.chore,
            member=self.member,
            due_date=timezone.now().date(),
        )
        self.assertEqual(Assignment.objects.count(), 1)
        self.member.delete()
        self.assertEqual(Assignment.objects.count(), 0)

    def test_cascade_deletion_on_chore_delete(self):
        Assignment.objects.create(
            chore=self.chore,
            member=self.member,
            due_date=timezone.now().date(),
        )
        self.assertEqual(Assignment.objects.count(), 1)
        self.chore.delete()
        self.assertEqual(Assignment.objects.count(), 0)


class SeedChoresCommandTests(TestCase):
    """Tests covering the seed_chores management command."""

    def test_seed_chores_from_empty_database(self):
        Member.objects.all().delete()
        Chore.objects.all().delete()
        call_command('seed_chores')
        self.assertEqual(Member.objects.count(), 3)
        self.assertEqual(Chore.objects.count(), 5)

    def test_seed_chores_idempotence(self):
        """Running seed_chores multiple times does not produce duplicate records."""
        call_command('seed_chores')
        initial_members = Member.objects.count()
        initial_chores = Chore.objects.count()

        # Run again
        call_command('seed_chores')
        self.assertEqual(Member.objects.count(), initial_members)
        self.assertEqual(Chore.objects.count(), initial_chores)


class AdminRegistrationTests(TestCase):
    """Tests verifying model registration in the Django admin site."""

    def test_models_registered_in_admin(self):
        self.assertIn(Member, admin.site._registry)
        self.assertIn(Chore, admin.site._registry)
        self.assertIn(Assignment, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Member], MemberAdmin)
        self.assertIsInstance(admin.site._registry[Chore], ChoreAdmin)
        self.assertIsInstance(admin.site._registry[Assignment], AssignmentAdmin)
