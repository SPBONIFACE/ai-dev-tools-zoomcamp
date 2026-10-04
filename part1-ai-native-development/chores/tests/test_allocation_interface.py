import json
from unittest import TestCase
from pydantic import ValidationError

from chores.allocation.schemas import (
    MemberData,
    ChoreData,
    WorkloadHistory,
    ProposedAssignment,
    AllocationRequest,
    AllocationResponse,
    InvalidAllocationRequestError,
)
from chores.allocation.interface import BaseAllocationEngine


class AllocationSchemasTests(TestCase):
    """Unit tests verifying Pydantic schema instantiation and serialization."""

    def test_member_data_instantiation(self):
        member = MemberData(id=1, name="Alice")
        self.assertEqual(member.id, 1)
        self.assertEqual(member.name, "Alice")

    def test_chore_data_valid_effort_levels(self):
        for effort in [1, 2, 3]:
            chore = ChoreData(id=1, title="Clean Kitchen", effort_level=effort, frequency="daily")
            self.assertEqual(chore.effort_level, effort)

    def test_chore_data_invalid_effort_level_low(self):
        with self.assertRaises((InvalidAllocationRequestError, ValidationError)):
            ChoreData(id=1, title="Clean Kitchen", effort_level=0, frequency="daily")

    def test_chore_data_invalid_effort_level_high(self):
        with self.assertRaises((InvalidAllocationRequestError, ValidationError)):
            ChoreData(id=1, title="Clean Kitchen", effort_level=4, frequency="daily")

    def test_workload_history_instantiation_and_defaults(self):
        history_default = WorkloadHistory(member_id=2)
        self.assertEqual(history_default.member_id, 2)
        self.assertEqual(history_default.recent_effort_sum, 0)

        history_custom = WorkloadHistory(member_id=2, recent_effort_sum=7)
        self.assertEqual(history_custom.recent_effort_sum, 7)

    def test_proposed_assignment_instantiation(self):
        assignment = ProposedAssignment(
            chore_id=10,
            member_id=1,
            reasoning="Alice volunteered for kitchen duty",
        )
        self.assertEqual(assignment.chore_id, 10)
        self.assertEqual(assignment.member_id, 1)
        self.assertEqual(assignment.reasoning, "Alice volunteered for kitchen duty")

    def test_allocation_request_instantiation(self):
        member = MemberData(id=1, name="Alice")
        chore = ChoreData(id=10, title="Dusting", effort_level=1, frequency="weekly")
        req = AllocationRequest(
            members=[member],
            chores=[chore],
            workload_history=[WorkloadHistory(member_id=1, recent_effort_sum=2)],
            user_notes="Alice has exams",
        )
        self.assertEqual(len(req.members), 1)
        self.assertEqual(len(req.chores), 1)
        self.assertEqual(len(req.workload_history), 1)
        self.assertEqual(req.user_notes, "Alice has exams")

    def test_allocation_request_serialization_and_deserialization(self):
        req = AllocationRequest(
            members=[MemberData(id=1, name="Alice"), MemberData(id=2, name="Bob")],
            chores=[ChoreData(id=1, title="Wash Dishes", effort_level=2, frequency="daily")],
            workload_history=[WorkloadHistory(member_id=1, recent_effort_sum=3)],
            user_notes="Bob is free all week",
        )

        # JSON round-trip
        json_data = req.model_dump_json()
        deserialized = AllocationRequest.model_validate_json(json_data)
        self.assertEqual(req, deserialized)

        # Dict round-trip
        dict_data = req.model_dump()
        from_dict = AllocationRequest.model_validate(dict_data)
        self.assertEqual(req, from_dict)

    def test_allocation_response_serialization_and_deserialization(self):
        res = AllocationResponse(
            assignments=[
                ProposedAssignment(chore_id=1, member_id=2, reasoning="Bob is free"),
            ],
            raw_reasoning_summary="Balanced workload across 2 members.",
            engine_used="mock",
        )

        json_data = res.model_dump_json()
        deserialized = AllocationResponse.model_validate_json(json_data)
        self.assertEqual(res, deserialized)


class AllocationValidationEdgeCasesTests(TestCase):
    """Unit tests verifying edge cases and validation rules."""

    def test_empty_members_raises_error(self):
        chore = ChoreData(id=1, title="Trash", effort_level=1, frequency="daily")
        with self.assertRaises(InvalidAllocationRequestError) as ctx:
            AllocationRequest(members=[], chores=[chore])

        self.assertIn("Cannot allocate chores with zero household members.", str(ctx.exception))

    def test_empty_chores_is_allowed(self):
        member = MemberData(id=1, name="Alice")
        req = AllocationRequest(members=[member], chores=[])
        self.assertEqual(req.chores, [])

    def test_user_notes_defaults_and_normalization(self):
        member = MemberData(id=1, name="Alice")

        # Default when omitted
        req_default = AllocationRequest(members=[member])
        self.assertEqual(req_default.user_notes, "")

        # When None provided
        req_none = AllocationRequest(members=[member], user_notes=None)
        self.assertEqual(req_none.user_notes, "")

        # When whitespace provided
        req_whitespace = AllocationRequest(members=[member], user_notes="   \t\n ")
        self.assertEqual(req_whitespace.user_notes, "")

        # When valid text provided
        req_text = AllocationRequest(members=[member], user_notes="Charlie traveling")
        self.assertEqual(req_text.user_notes, "Charlie traveling")


class BaseAllocationEngineInterfaceTests(TestCase):
    """Unit tests verifying the BaseAllocationEngine contract."""

    def test_cannot_instantiate_abstract_base_engine(self):
        with self.assertRaises(TypeError):
            BaseAllocationEngine()

    def test_concrete_engine_implementation(self):
        class TestEngine(BaseAllocationEngine):
            def allocate(self, request: AllocationRequest) -> AllocationResponse:
                if not request.chores:
                    return AllocationResponse(
                        assignments=[],
                        raw_reasoning_summary="No active chores to allocate.",
                        engine_used="mock",
                    )
                assignments = [
                    ProposedAssignment(
                        chore_id=chore.id,
                        member_id=request.members[0].id,
                        reasoning=f"Assigned to {request.members[0].name}",
                    )
                    for chore in request.chores
                ]
                return AllocationResponse(
                    assignments=assignments,
                    raw_reasoning_summary="Assigned all chores to first member.",
                    engine_used="mock",
                )

        engine = TestEngine()
        member = MemberData(id=1, name="Alice")

        # Empty chores edge case
        req_empty = AllocationRequest(members=[member], chores=[])
        res_empty = engine.allocate(req_empty)
        self.assertEqual(res_empty.assignments, [])
        self.assertEqual(res_empty.raw_reasoning_summary, "No active chores to allocate.")
        self.assertEqual(res_empty.engine_used, "mock")

        # Standard allocation
        chore = ChoreData(id=1, title="Vacuum", effort_level=2, frequency="weekly")
        req = AllocationRequest(members=[member], chores=[chore])
        res = engine.allocate(req)
        self.assertEqual(len(res.assignments), 1)
        self.assertEqual(res.assignments[0].chore_id, 1)
        self.assertEqual(res.assignments[0].member_id, 1)
        self.assertEqual(res.assignments[0].reasoning, "Assigned to Alice")
