from unittest import TestCase
from chores.allocation.interface import BaseAllocationEngine
from chores.allocation.mock_engine import MockAllocationEngine, parse_unavailable_members
from chores.allocation.schemas import (
    AllocationRequest,
    AllocationResponse,
    ChoreData,
    InvalidAllocationRequestError,
    MemberData,
    WorkloadHistory,
)


class MockAllocationEngineInheritanceTests(TestCase):
    """Tests for MockAllocationEngine class definition and inheritance."""

    def test_inherits_from_base_allocation_engine(self):
        self.assertTrue(issubclass(MockAllocationEngine, BaseAllocationEngine))
        engine = MockAllocationEngine()
        self.assertIsInstance(engine, BaseAllocationEngine)


class MockAllocationEngineAllocationTests(TestCase):
    """Tests verifying deterministic allocation, effort balancing, tie breaking, and notes parsing."""

    def setUp(self):
        self.engine = MockAllocationEngine()
        self.alice = MemberData(id=1, name="Alice")
        self.bob = MemberData(id=2, name="Bob")
        self.charlie = MemberData(id=3, name="Charlie")
        self.members = [self.alice, self.bob, self.charlie]

    def test_allocate_returns_valid_allocation_response(self):
        chores = [
            ChoreData(id=1, title="Dishes", effort_level=2, frequency="daily"),
        ]
        req = AllocationRequest(members=self.members, chores=chores)
        res = self.engine.allocate(req)

        self.assertIsInstance(res, AllocationResponse)
        self.assertEqual(res.engine_used, "mock")
        self.assertEqual(len(res.assignments), 1)
        self.assertEqual(res.assignments[0].chore_id, 1)
        self.assertEqual(res.assignments[0].member_id, self.alice.id)
        self.assertIn("Assigned to Alice based on lowest current workload score", res.assignments[0].reasoning)
        self.assertTrue(len(res.raw_reasoning_summary) > 0)

    def test_empty_chores_returns_empty_assignments(self):
        req = AllocationRequest(members=self.members, chores=[])
        res = self.engine.allocate(req)

        self.assertIsInstance(res, AllocationResponse)
        self.assertEqual(res.assignments, [])
        self.assertEqual(res.raw_reasoning_summary, "No active chores to allocate.")
        self.assertEqual(res.engine_used, "mock")

    def test_invalid_request_type_raises_error(self):
        with self.assertRaises(InvalidAllocationRequestError):
            self.engine.allocate("not an allocation request")  # type: ignore

    def test_equal_effort_distribution_on_balanced_roster(self):
        # 3 members, 3 chores with effort 2 -> each member gets exactly 1 chore (2 pts each)
        chores = [
            ChoreData(id=1, title="Vacuum", effort_level=2, frequency="weekly"),
            ChoreData(id=2, title="Mop", effort_level=2, frequency="weekly"),
            ChoreData(id=3, title="Dust", effort_level=2, frequency="weekly"),
        ]
        req = AllocationRequest(members=self.members, chores=chores)
        res = self.engine.allocate(req)

        assigned_members = [a.member_id for a in res.assignments]
        self.assertCountEqual(assigned_members, [self.alice.id, self.bob.id, self.charlie.id])

        # Verify each member gets 1 chore and 2 points
        member_workloads = {m.id: 0 for m in self.members}
        for a in res.assignments:
            chore = next(c for c in chores if c.id == a.chore_id)
            member_workloads[a.member_id] += chore.effort_level

        for m_id, points in member_workloads.items():
            self.assertEqual(points, 2)

    def test_effort_sorted_descending_heaviest_first(self):
        # Chores with effort levels: 1, 3, 2
        chores = [
            ChoreData(id=10, title="Light task", effort_level=1, frequency="daily"),
            ChoreData(id=20, title="Heavy task", effort_level=3, frequency="weekly"),
            ChoreData(id=30, title="Medium task", effort_level=2, frequency="daily"),
        ]
        req = AllocationRequest(members=self.members, chores=chores)
        res = self.engine.allocate(req)

        # First assigned chore should be the heaviest (id=20, effort=3) to Alice (alphabetical tie-breaker at 0)
        self.assertEqual(res.assignments[0].chore_id, 20)
        self.assertEqual(res.assignments[0].member_id, self.alice.id)
        # Second assigned chore should be effort 2 (id=30) to Bob (workload 0 < Alice 3)
        self.assertEqual(res.assignments[1].chore_id, 30)
        self.assertEqual(res.assignments[1].member_id, self.bob.id)
        # Third assigned chore should be effort 1 (id=10) to Charlie (workload 0 < Bob 2 < Alice 3)
        self.assertEqual(res.assignments[2].chore_id, 10)
        self.assertEqual(res.assignments[2].member_id, self.charlie.id)

    def test_deterministic_tie_breaking_alphabetical(self):
        # Two members with identical workload: Bob and Alice.
        # Alice should win tie break alphabetically.
        members = [MemberData(id=2, name="Bob"), MemberData(id=1, name="Alice")]
        chores = [ChoreData(id=1, title="Kitchen", effort_level=1, frequency="daily")]
        req = AllocationRequest(members=members, chores=chores)
        res = self.engine.allocate(req)

        self.assertEqual(res.assignments[0].member_id, 1)  # Alice
        self.assertIn("Assigned to Alice based on lowest current workload score (0 pts) and availability.", res.assignments[0].reasoning)

    def test_workload_history_incorporation(self):
        # Alice already has 5 points, Bob has 2 points, Charlie has 0 points
        history = [
            WorkloadHistory(member_id=self.alice.id, recent_effort_sum=5),
            WorkloadHistory(member_id=self.bob.id, recent_effort_sum=2),
            WorkloadHistory(member_id=self.charlie.id, recent_effort_sum=0),
        ]
        chore = ChoreData(id=1, title="Trash", effort_level=1, frequency="daily")
        req = AllocationRequest(members=self.members, chores=[chore], workload_history=history)
        res = self.engine.allocate(req)

        # Charlie has lowest score (0)
        self.assertEqual(res.assignments[0].member_id, self.charlie.id)
        self.assertIn("lowest current workload score (0 pts)", res.assignments[0].reasoning)

    def test_omitted_or_partial_workload_history(self):
        # Workload history only includes Bob with 3 pts; Alice and Charlie default to 0
        history = [WorkloadHistory(member_id=self.bob.id, recent_effort_sum=3)]
        chore = ChoreData(id=1, title="Dishes", effort_level=1, frequency="daily")
        req = AllocationRequest(members=self.members, chores=[chore], workload_history=history)
        res = self.engine.allocate(req)

        # Alice and Charlie tied at 0, Alice wins alphabetically
        self.assertEqual(res.assignments[0].member_id, self.alice.id)

    def test_exclusion_of_unavailable_members_via_user_notes(self):
        # Alice is away -> only Bob and Charlie should receive chores
        chores = [
            ChoreData(id=1, title="Chore 1", effort_level=2, frequency="daily"),
            ChoreData(id=2, title="Chore 2", effort_level=2, frequency="daily"),
        ]
        req = AllocationRequest(
            members=self.members,
            chores=chores,
            user_notes="Alice is away this week.",
        )
        res = self.engine.allocate(req)

        assigned_member_ids = {a.member_id for a in res.assignments}
        self.assertNotIn(self.alice.id, assigned_member_ids)
        self.assertIn(self.bob.id, assigned_member_ids)
        self.assertIn(self.charlie.id, assigned_member_ids)

    def test_various_negative_indicator_keywords(self):
        keywords_and_phrases = [
            ("Alice is away", self.alice.id),
            ("Bob is busy with exams", self.bob.id),
            ("Charlie is on vacation", self.charlie.id),
            ("Alice is out of town until Friday", self.alice.id),
            ("Bob is traveling for work", self.bob.id),
            ("Charlie is sick today", self.charlie.id),
            ("Alice is unavailable", self.alice.id),
            ("Bob is not available", self.bob.id),
        ]
        chore = ChoreData(id=1, title="Clean", effort_level=1, frequency="daily")

        for note, excluded_id in keywords_and_phrases:
            with self.subTest(note=note):
                req = AllocationRequest(members=self.members, chores=[chore], user_notes=note)
                res = self.engine.allocate(req)
                self.assertNotEqual(res.assignments[0].member_id, excluded_id)

    def test_multiple_members_unavailable_in_notes(self):
        chores = [
            ChoreData(id=1, title="Chore 1", effort_level=2, frequency="daily"),
            ChoreData(id=2, title="Chore 2", effort_level=2, frequency="daily"),
        ]
        # Alice and Bob unavailable
        req = AllocationRequest(
            members=self.members,
            chores=chores,
            user_notes="Alice is away and Bob is sick",
        )
        res = self.engine.allocate(req)

        # Only Charlie should get all chores
        for a in res.assignments:
            self.assertEqual(a.member_id, self.charlie.id)

    def test_fallback_behavior_when_all_members_are_unavailable(self):
        chores = [
            ChoreData(id=1, title="Chore 1", effort_level=2, frequency="daily"),
            ChoreData(id=2, title="Chore 2", effort_level=2, frequency="daily"),
            ChoreData(id=3, title="Chore 3", effort_level=2, frequency="daily"),
        ]
        req = AllocationRequest(
            members=self.members,
            chores=chores,
            user_notes="Alice is away, Bob is away, Charlie is sick",
        )
        with self.assertLogs("chores.allocation.mock_engine", level="WARNING") as cm:
            res = self.engine.allocate(req)

        # Verify fallback warning was logged
        self.assertTrue(any("All members were marked unavailable in notes" in msg for msg in cm.output))

        # Verify raw_reasoning_summary contains exact fallback message
        expected_fallback = "All members were marked unavailable in notes; falling back to full roster allocation."
        self.assertIn(expected_fallback, res.raw_reasoning_summary)

        # Verify all members were considered and assigned
        assigned_ids = {a.member_id for a in res.assignments}
        self.assertEqual(assigned_ids, {self.alice.id, self.bob.id, self.charlie.id})

    def test_partial_name_matching_avoidance(self):
        # Member 'Al' should not match 'Also' or 'Alan'
        al = MemberData(id=10, name="Al")
        bob = MemberData(id=2, name="Bob")
        chores = [ChoreData(id=1, title="Trash", effort_level=1, frequency="daily")]

        # 'Also, Bob is away' -> Bob is away, but Al is NOT
        req = AllocationRequest(members=[al, bob], chores=chores, user_notes="Also, Bob is away")
        res = self.engine.allocate(req)
        self.assertEqual(res.assignments[0].member_id, al.id)

        # 'Alan is away' -> neither Al nor Bob is Alan
        req2 = AllocationRequest(members=[al, bob], chores=chores, user_notes="Alan is away")
        res2 = self.engine.allocate(req2)
        # Al wins tie break against Bob
        self.assertEqual(res2.assignments[0].member_id, al.id)

    def test_deterministic_repeatability(self):
        chores = [
            ChoreData(id=1, title="Kitchen", effort_level=3, frequency="daily"),
            ChoreData(id=2, title="Bathrooms", effort_level=3, frequency="weekly"),
            ChoreData(id=3, title="Groceries", effort_level=2, frequency="weekly"),
            ChoreData(id=4, title="Trash", effort_level=1, frequency="daily"),
            ChoreData(id=5, title="Vacuum", effort_level=2, frequency="weekly"),
        ]
        history = [
            WorkloadHistory(member_id=self.alice.id, recent_effort_sum=4),
            WorkloadHistory(member_id=self.bob.id, recent_effort_sum=1),
            WorkloadHistory(member_id=self.charlie.id, recent_effort_sum=3),
        ]
        req = AllocationRequest(
            members=self.members,
            chores=chores,
            workload_history=history,
            user_notes="Charlie has exams but is free on weekends",
        )

        # Run 5 times and check results are identical
        results = [self.engine.allocate(req) for _ in range(5)]
        first_result = results[0]

        for subsequent_result in results[1:]:
            self.assertEqual(first_result.model_dump(), subsequent_result.model_dump())

    def test_response_json_serialization(self):
        chores = [ChoreData(id=1, title="Vacuum", effort_level=1, frequency="weekly")]
        req = AllocationRequest(members=self.members, chores=chores)
        res = self.engine.allocate(req)

        json_str = res.model_dump_json()
        deserialized = AllocationResponse.model_validate_json(json_str)
        self.assertEqual(res, deserialized)
