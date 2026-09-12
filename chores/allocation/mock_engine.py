import logging
import re
from typing import List, Set

from chores.allocation.interface import BaseAllocationEngine
from chores.allocation.schemas import (
    AllocationRequest,
    AllocationResponse,
    InvalidAllocationRequestError,
    MemberData,
    ProposedAssignment,
)

logger = logging.getLogger(__name__)

NEGATIVE_INDICATORS = [
    r"away",
    r"busy",
    r"vacation",
    r"out\s+of\s+town",
    r"out\s+of\s+office",
    r"traveling",
    r"travelling",
    r"sick",
    r"unavailable",
    r"not\s+available",
    r"unwell",
    r"on\s+leave",
]

INDICATOR_PATTERN = r"(?:\b(?:" + "|".join(NEGATIVE_INDICATORS) + r")\b)"


def parse_unavailable_members(members: List[MemberData], user_notes: str) -> Set[int]:
    """
    Parse user notes using case-insensitive heuristic pattern matching
    to identify members who are unavailable.
    """
    if not user_notes or not user_notes.strip():
        return set()

    unavailable: Set[int] = set()
    all_names = [re.escape(m.name) for m in members]
    all_names_pattern = r"(?:" + "|".join(all_names) + r")"

    sentences = re.split(r"[.\n\r;!?]+", user_notes)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if not re.search(INDICATOR_PATTERN, sentence, re.IGNORECASE):
            continue

        for m in members:
            m_name = m.name
            m_id = m.id
            other_names = [re.escape(other.name) for other in members if other.id != m_id]
            other_pattern = r"(?:\b(?:" + "|".join(other_names) + r")\b)" if other_names else r"(?!)"

            # Rule 1: Member followed by indicator without another member or clause boundary in between
            p1 = rf"\b{re.escape(m_name)}\b(?:(?!\b{other_pattern}\b)[^,;!?\n])*?{INDICATOR_PATTERN}"
            if re.search(p1, sentence, re.IGNORECASE):
                unavailable.add(m_id)
                continue

            # Rule 2: Indicator followed by member without another member or clause boundary in between
            p2 = rf"{INDICATOR_PATTERN}\s*[:=-]?\s*(?:(?!\b{other_pattern}\b)[^,;!?\n])*?\b{re.escape(m_name)}\b"
            if re.search(p2, sentence, re.IGNORECASE):
                unavailable.add(m_id)
                continue

            # Rule 3: Member in coordinated list before indicator (e.g. Alice and Bob are away)
            coord_before = (
                rf"\b{re.escape(m_name)}\b(?:\s*,\s*|\s+and\s+|\s+or\s+|\b{all_names_pattern}\b|\s+)+"
                rf"(?:are|is|all|both|will be|on)?\s*[^.!?;\n,]*?{INDICATOR_PATTERN}"
            )
            if re.search(coord_before, sentence, re.IGNORECASE):
                unavailable.add(m_id)
                continue

            # Rule 4: Indicator prefix followed by colon/dash and list containing member (e.g. Away: Alice, Bob)
            coord_after = rf"{INDICATOR_PATTERN}\s*[:=-]\s*[^.!?;\n]*?\b{re.escape(m_name)}\b"
            if re.search(coord_after, sentence, re.IGNORECASE):
                unavailable.add(m_id)
                continue

    return unavailable


class MockAllocationEngine(BaseAllocationEngine):
    """
    Deterministic rule-based chore allocation engine.
    Fairly balances effort points across available household members and respects
    availability constraints parsed from user natural language notes.
    """

    def allocate(self, request: AllocationRequest) -> AllocationResponse:
        """
        Deterministically allocate chores to members based on workload history,
        effort points, and natural language availability constraints.
        """
        if not isinstance(request, AllocationRequest):
            raise InvalidAllocationRequestError(f"Expected AllocationRequest, got {type(request).__name__}")

        if not request.members:
            raise InvalidAllocationRequestError("Cannot allocate chores with zero household members.")

        if not request.chores:
            return AllocationResponse(
                assignments=[],
                raw_reasoning_summary="No active chores to allocate.",
                engine_used="mock",
            )

        # 1. Starting Workload Calculation
        workload: dict[int, int] = {m.id: 0 for m in request.members}
        for wh in request.workload_history:
            if wh.member_id in workload:
                workload[wh.member_id] = wh.recent_effort_sum

        # 2. Availability & Constraint Parsing (Heuristic)
        unavailable_ids = parse_unavailable_members(request.members, request.user_notes or "")
        all_members_unavailable = len(unavailable_ids) == len(request.members)

        if all_members_unavailable:
            logger.warning("All members were marked unavailable in notes; falling back to full roster allocation.")
            available_members = list(request.members)
            raw_reasoning_summary = "All members were marked unavailable in notes; falling back to full roster allocation."
        else:
            available_members = [m for m in request.members if m.id not in unavailable_ids]
            if unavailable_ids:
                raw_reasoning_summary = (
                    f"Balanced {len(request.chores)} chores across {len(available_members)} available member(s). "
                    f"Excluded {len(unavailable_ids)} unavailable member(s) based on notes."
                )
            else:
                raw_reasoning_summary = (
                    f"Balanced {len(request.chores)} chores across {len(available_members)} member(s) deterministically."
                )

        # 3. Deterministic Chore Sorting & Assignment
        # Sort chores by effort_level descending (heaviest chores first)
        sorted_chores = sorted(request.chores, key=lambda c: c.effort_level, reverse=True)

        assignments: List[ProposedAssignment] = []
        for chore in sorted_chores:
            # Pick available member with lowest accumulated workload points.
            # Break ties deterministically by alphabetical order of member.name.
            selected_member = min(
                available_members,
                key=lambda m: (workload[m.id], m.name.lower(), m.name, m.id),
            )
            current_workload = workload[selected_member.id]
            workload[selected_member.id] += chore.effort_level

            assignments.append(
                ProposedAssignment(
                    chore_id=chore.id,
                    member_id=selected_member.id,
                    reasoning=(
                        f"Assigned to {selected_member.name} based on lowest current workload score "
                        f"({current_workload} pts) and availability."
                    ),
                )
            )

        return AllocationResponse(
            assignments=assignments,
            raw_reasoning_summary=raw_reasoning_summary,
            engine_used="mock",
        )
