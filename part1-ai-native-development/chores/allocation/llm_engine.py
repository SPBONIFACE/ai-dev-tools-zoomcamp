import json
import logging
import os
import urllib.error
import urllib.request
from typing import List, Optional

from django.conf import settings
from pydantic import ValidationError

from chores.allocation.interface import BaseAllocationEngine
from chores.allocation.mock_engine import MockAllocationEngine
from chores.allocation.schemas import (
    AllocationRequest,
    AllocationResponse,
    InvalidAllocationRequestError,
    ProposedAssignment,
)

logger = logging.getLogger(__name__)


def _clean_json_text(raw_text: str) -> str:
    """
    Clean raw LLM response text by stripping markdown code fences if present.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        else:
            text = ""
        text = text.rstrip()
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


class LLMAllocationEngine(BaseAllocationEngine):
    """
    LLM-powered chore allocation engine with automatic fallback to MockAllocationEngine.
    Supports OpenAI, Gemini, Groq, and Mock providers.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ):
        resolved_provider = (
            provider
            or getattr(settings, "AI_PROVIDER", None)
            or os.environ.get("AI_PROVIDER")
            or "openai"
        )
        self.provider = str(resolved_provider).lower().strip()

        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = self._resolve_api_key(self.provider)

        resolved_model = (
            model
            or getattr(settings, "AI_MODEL", None)
            or os.environ.get("AI_MODEL")
            or self._default_model_for_provider(self.provider)
        )
        self.model = str(resolved_model).strip()

        timeout_val = getattr(settings, "AI_TIMEOUT", None) or os.environ.get("AI_TIMEOUT")
        if timeout_val is not None:
            try:
                self.timeout = int(timeout_val)
            except (ValueError, TypeError):
                self.timeout = timeout
        else:
            self.timeout = timeout

        self._mock_engine = MockAllocationEngine()

    def _resolve_api_key(self, provider: str) -> Optional[str]:
        """
        Resolve the API key for the specified provider from Django settings or environment variables.
        """
        key_var = f"{provider.upper()}_API_KEY"
        key = getattr(settings, key_var, None) or os.environ.get(key_var)
        if key is not None and str(key).strip():
            return str(key).strip()

        # Fallback to generic AI_API_KEY
        generic_key = getattr(settings, "AI_API_KEY", None) or os.environ.get("AI_API_KEY")
        if generic_key is not None and str(generic_key).strip():
            return str(generic_key).strip()

        return None

    def _default_model_for_provider(self, provider: str) -> str:
        """
        Return the default model name for the given provider.
        """
        if provider == "openai":
            return "gpt-4o-mini"
        elif provider == "gemini":
            return "gemini-1.5-flash"
        elif provider == "groq":
            return "llama-3.3-70b-versatile"
        return "default"

    def build_prompt(self, request: AllocationRequest) -> str:
        """
        Build a structured prompt incorporating household member roster, active chores,
        workload history, user natural language notes, and JSON schema output instructions.
        """
        members_data = [{"id": m.id, "name": m.name} for m in request.members]
        chores_data = [
            {
                "id": c.id,
                "title": c.title,
                "effort_level": c.effort_level,
                "frequency": c.frequency,
            }
            for c in request.chores
        ]
        workload_data = [
            {"member_id": wh.member_id, "recent_effort_sum": wh.recent_effort_sum}
            for wh in request.workload_history
        ]
        user_notes = request.user_notes if request.user_notes else "None"

        return f"""You are an intelligent household chore allocation engine.
Assign every chore to exactly one household member fairly.

Household Members (Roster):
{json.dumps(members_data, indent=2)}

Active Chores:
{json.dumps(chores_data, indent=2)}

Past Workload History (Effort points accumulated recently):
{json.dumps(workload_data, indent=2)}

User Notes & Availability Constraints:
{user_notes}

Instructions:
1. Assign every chore in the list to an available household member.
2. Fairly balance total effort points, accounting for past workload history and the effort level of each chore (1=Low, 2=Medium, 3=High).
3. Strictly adhere to availability constraints or preferences mentioned in the User Notes (e.g., away, busy, sick).
4. Every chore must be assigned to exactly one member. Only use member IDs and chore IDs present in the input.
5. Return ONLY a valid JSON object matching this schema:
{{
  "assignments": [
    {{
      "chore_id": <int>,
      "member_id": <int>,
      "reasoning": "<string explanation for why this member was assigned this chore>"
    }}
  ],
  "raw_reasoning_summary": "<string overall summary of workload balancing and availability consideration>"
}}
""".strip()

    def _call_provider(self, prompt: str) -> str:
        """
        Execute API call to the configured AI provider and return the raw text response.
        """
        if self.provider in ("openai", "groq"):
            endpoint = (
                "https://api.openai.com/v1/chat/completions"
                if self.provider == "openai"
                else "https://api.groq.com/openai/v1/chat/completions"
            )
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "ChoreManager/1.0",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an AI chore allocation assistant. "
                            "Assign chores fairly to household members and return only valid JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            }
            req = urllib.request.Request(
                url=endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]

        elif self.provider == "gemini":
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ChoreManager/1.0",
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    "You are an AI chore allocation assistant. "
                                    "Assign chores fairly and output only valid JSON matching the requested schema.\n\n"
                                    + prompt
                                )
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2,
                },
            }
            req = urllib.request.Request(
                url=endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]

        else:
            raise ValueError(
                f"Unsupported AI_PROVIDER: '{self.provider}'. Supported providers: openai, gemini, groq, mock."
            )

    def _parse_and_validate_response(
        self, response_text: str, request: AllocationRequest
    ) -> AllocationResponse:
        """
        Parse raw response text as JSON, validate with Pydantic, and verify chore/member ID consistency.
        """
        cleaned_text = _clean_json_text(response_text)
        try:
            data = json.loads(cleaned_text)
        except Exception as exc:
            raise ValueError(f"Failed to parse LLM response as JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("LLM response must be a JSON object.")

        raw_assignments = data.get("assignments")
        if not isinstance(raw_assignments, list):
            raise ValueError("LLM response missing 'assignments' list.")

        raw_summary = data.get("raw_reasoning_summary", "")
        if not isinstance(raw_summary, str):
            raw_summary = str(raw_summary)

        valid_member_ids = {m.id for m in request.members}
        valid_chore_ids = {c.id for c in request.chores}

        parsed_assignments: List[ProposedAssignment] = []
        assigned_chore_ids = set()

        for item in raw_assignments:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid assignment item (expected dict): {item}")
            try:
                assignment = ProposedAssignment.model_validate(item)
            except ValidationError as ve:
                raise ValueError(f"Invalid assignment schema: {ve}") from ve

            if assignment.member_id not in valid_member_ids:
                raise ValueError(
                    f"LLM assigned chore to unknown member_id {assignment.member_id} "
                    f"(valid IDs: {valid_member_ids})"
                )
            if assignment.chore_id not in valid_chore_ids:
                raise ValueError(
                    f"LLM assigned unknown chore_id {assignment.chore_id} "
                    f"(valid IDs: {valid_chore_ids})"
                )
            if assignment.chore_id in assigned_chore_ids:
                raise ValueError(f"Duplicate assignment for chore_id {assignment.chore_id}")

            assigned_chore_ids.add(assignment.chore_id)
            parsed_assignments.append(assignment)

        if assigned_chore_ids != valid_chore_ids:
            missing = valid_chore_ids - assigned_chore_ids
            raise ValueError(f"LLM failed to assign all chores. Missing chore IDs: {missing}")

        return AllocationResponse(
            assignments=parsed_assignments,
            raw_reasoning_summary=raw_summary,
            engine_used="llm",
        )

    def allocate(self, request: AllocationRequest) -> AllocationResponse:
        """
        Allocate chores to members using the configured LLM provider.
        Gracefully falls back to MockAllocationEngine on missing API key or any failure.
        """
        if not isinstance(request, AllocationRequest):
            raise InvalidAllocationRequestError(
                f"Expected AllocationRequest, got {type(request).__name__}"
            )

        if not request.members:
            raise InvalidAllocationRequestError(
                "Cannot allocate chores with zero household members."
            )

        # 1. Configured mock mode
        if self.provider == "mock":
            logger.info("AI_PROVIDER is 'mock'; delegating to MockAllocationEngine.")
            return self._mock_engine.allocate(request)

        # 2. Missing API key triggers immediate fallback
        if not self.api_key:
            logger.info(
                "No API key configured for AI_PROVIDER '%s'; falling back to MockAllocationEngine.",
                self.provider,
            )
            fallback_response = self._mock_engine.allocate(request)
            fallback_response.engine_used = "mock (fallback)"
            return fallback_response

        # 3. Empty chores edge case
        if not request.chores:
            return AllocationResponse(
                assignments=[],
                raw_reasoning_summary="No active chores to allocate.",
                engine_used="llm",
            )

        # 4. Attempt LLM allocation with fallback
        try:
            prompt = self.build_prompt(request)
            response_text = self._call_provider(prompt)
            return self._parse_and_validate_response(response_text, request)
        except Exception as exc:
            logger.warning(
                "LLM allocation failed (%s: %s); falling back to MockAllocationEngine.",
                type(exc).__name__,
                str(exc),
                exc_info=True,
            )
            fallback_response = self._mock_engine.allocate(request)
            fallback_response.engine_used = "mock (fallback)"
            return fallback_response
