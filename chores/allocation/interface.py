from abc import ABC, abstractmethod
from chores.allocation.schemas import (
    AllocationRequest,
    AllocationResponse,
    InvalidAllocationRequestError,
)


class BaseAllocationEngine(ABC):
    """
    Abstract base class defining the contract for chore allocation engines.
    """

    @abstractmethod
    def allocate(self, request: AllocationRequest) -> AllocationResponse:
        """
        Allocate chores to members based on the provided request.

        :param request: Validated AllocationRequest containing members, chores, workload history, and notes.
        :return: AllocationResponse containing proposed assignments and reasoning summary.
        :raises InvalidAllocationRequestError: If the request is invalid.
        """
        pass
