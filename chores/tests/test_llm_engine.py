import json
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from django.test import override_settings

from chores.allocation.interface import BaseAllocationEngine
from chores.allocation.llm_engine import LLMAllocationEngine
from chores.allocation.schemas import (
    AllocationRequest,
    AllocationResponse,
    ChoreData,
    InvalidAllocationRequestError,
    MemberData,
    WorkloadHistory,
)


class LLMAllocationEngineInheritanceTests(TestCase):
    """Tests verifying inheritance and interface compliance."""

    def test_inherits_from_base_allocation_engine(self):
        self.assertTrue(issubclass(LLMAllocationEngine, BaseAllocationEngine))
        engine = LLMAllocationEngine(provider="mock")
        self.assertIsInstance(engine, BaseAllocationEngine)


class LLMAllocationEnginePromptTests(TestCase):
    """Tests verifying prompt generation and schema formatting."""

    def setUp(self):
        self.engine = LLMAllocationEngine(provider="openai", api_key="sk-test-key")
        self.members = [
            MemberData(id=1, name="Alice"),
            MemberData(id=2, name="Bob"),
        ]
        self.chores = [
            ChoreData(id=10, title="Wash Dishes", effort_level=2, frequency="daily"),
            ChoreData(id=20, title="Vacuum Living Room", effort_level=1, frequency="weekly"),
        ]
        self.history = [
            WorkloadHistory(member_id=1, recent_effort_sum=4),
            WorkloadHistory(member_id=2, recent_effort_sum=1),
        ]

    def test_build_prompt_contains_all_input_components(self):
        req = AllocationRequest(
            members=self.members,
            chores=self.chores,
            workload_history=self.history,
            user_notes="Bob is away on Friday.",
        )
        prompt = self.engine.build_prompt(req)

        # Check roster
        self.assertIn("Alice", prompt)
        self.assertIn("Bob", prompt)
        self.assertIn('"id": 1', prompt)
        self.assertIn('"id": 2', prompt)

        # Check chores
        self.assertIn("Wash Dishes", prompt)
        self.assertIn("Vacuum Living Room", prompt)
        self.assertIn('"effort_level": 2', prompt)
        self.assertIn('"effort_level": 1', prompt)

        # Check workload history
        self.assertIn('"recent_effort_sum": 4', prompt)
        self.assertIn('"recent_effort_sum": 1', prompt)

        # Check user notes
        self.assertIn("Bob is away on Friday.", prompt)

    def test_build_prompt_specifies_json_schema(self):
        req = AllocationRequest(members=self.members, chores=self.chores)
        prompt = self.engine.build_prompt(req)

        self.assertIn('"assignments"', prompt)
        self.assertIn('"chore_id"', prompt)
        self.assertIn('"member_id"', prompt)
        self.assertIn('"reasoning"', prompt)
        self.assertIn('"raw_reasoning_summary"', prompt)


class LLMAllocationEngineSuccessfulAllocationTests(TestCase):
    """Tests verifying successful allocation across providers and response formats."""

    def setUp(self):
        self.members = [
            MemberData(id=1, name="Alice"),
            MemberData(id=2, name="Bob"),
        ]
        self.chores = [
            ChoreData(id=10, title="Dishes", effort_level=2, frequency="daily"),
            ChoreData(id=20, title="Vacuum", effort_level=1, frequency="weekly"),
        ]
        self.valid_response_payload = {
            "assignments": [
                {
                    "chore_id": 10,
                    "member_id": 1,
                    "reasoning": "Alice assigned dishes due to balanced effort.",
                },
                {
                    "chore_id": 20,
                    "member_id": 2,
                    "reasoning": "Bob assigned vacuum.",
                },
            ],
            "raw_reasoning_summary": "Assigned 2 chores fairly between Alice and Bob.",
        }

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_successful_allocation_openai(self, mock_call):
        mock_call.return_value = json.dumps(self.valid_response_payload)
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")

        req = AllocationRequest(members=self.members, chores=self.chores)
        res = engine.allocate(req)

        self.assertIsInstance(res, AllocationResponse)
        self.assertEqual(res.engine_used, "llm")
        self.assertEqual(len(res.assignments), 2)
        self.assertEqual(res.assignments[0].chore_id, 10)
        self.assertEqual(res.assignments[0].member_id, 1)
        self.assertEqual(res.assignments[1].chore_id, 20)
        self.assertEqual(res.assignments[1].member_id, 2)
        self.assertEqual(
            res.raw_reasoning_summary,
            "Assigned 2 chores fairly between Alice and Bob.",
        )
        mock_call.assert_called_once()

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_successful_allocation_with_markdown_code_fences(self, mock_call):
        raw_text = f"```json\n{json.dumps(self.valid_response_payload)}\n```"
        mock_call.return_value = raw_text
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")

        req = AllocationRequest(members=self.members, chores=self.chores)
        res = engine.allocate(req)

        self.assertEqual(res.engine_used, "llm")
        self.assertEqual(len(res.assignments), 2)

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_successful_allocation_gemini(self, mock_call):
        mock_call.return_value = json.dumps(self.valid_response_payload)
        engine = LLMAllocationEngine(provider="gemini", api_key="gemini-key")

        req = AllocationRequest(members=self.members, chores=self.chores)
        res = engine.allocate(req)

        self.assertEqual(res.engine_used, "llm")
        self.assertEqual(len(res.assignments), 2)

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_successful_allocation_groq(self, mock_call):
        mock_call.return_value = json.dumps(self.valid_response_payload)
        engine = LLMAllocationEngine(provider="groq", api_key="gsk-key")

        req = AllocationRequest(members=self.members, chores=self.chores)
        res = engine.allocate(req)

        self.assertEqual(res.engine_used, "llm")
        self.assertEqual(len(res.assignments), 2)

    def test_empty_chores_returns_early_without_calling_provider(self):
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=[])

        with patch.object(engine, "_call_provider") as mock_call:
            res = engine.allocate(req)
            mock_call.assert_not_called()

        self.assertEqual(res.assignments, [])
        self.assertEqual(res.raw_reasoning_summary, "No active chores to allocate.")
        self.assertEqual(res.engine_used, "llm")


class LLMAllocationEngineFallbackTests(TestCase):
    """Tests verifying robust fallback to MockAllocationEngine on errors, timeouts, or invalid data."""

    def setUp(self):
        self.alice = MemberData(id=1, name="Alice")
        self.bob = MemberData(id=2, name="Bob")
        self.members = [self.alice, self.bob]
        self.chores = [
            ChoreData(id=1, title="Dishes", effort_level=2, frequency="daily"),
            ChoreData(id=2, title="Trash", effort_level=1, frequency="daily"),
        ]

    def test_fallback_when_api_key_is_missing(self):
        engine = LLMAllocationEngine(provider="openai", api_key=None)
        req = AllocationRequest(members=self.members, chores=self.chores)

        with patch.object(engine, "_call_provider") as mock_call:
            res = engine.allocate(req)
            mock_call.assert_not_called()

        self.assertIsInstance(res, AllocationResponse)
        self.assertEqual(res.engine_used, "mock (fallback)")
        self.assertEqual(len(res.assignments), 2)

    def test_fallback_when_api_key_is_whitespace(self):
        engine = LLMAllocationEngine(provider="openai", api_key="   ")
        req = AllocationRequest(members=self.members, chores=self.chores)

        with patch.object(engine, "_call_provider") as mock_call:
            res = engine.allocate(req)
            mock_call.assert_not_called()

        self.assertEqual(res.engine_used, "mock (fallback)")

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_api_call_raises_timeout(self, mock_call):
        mock_call.side_effect = TimeoutError("Connection timed out")
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        with self.assertLogs("chores.allocation.llm_engine", level="WARNING") as cm:
            res = engine.allocate(req)

        self.assertEqual(res.engine_used, "mock (fallback)")
        self.assertEqual(len(res.assignments), 2)
        self.assertTrue(any("Connection timed out" in msg for msg in cm.output))

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_api_call_raises_network_error(self, mock_call):
        mock_call.side_effect = URLError("Network unreachable")
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")
        self.assertEqual(len(res.assignments), 2)

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_response_is_invalid_json(self, mock_call):
        mock_call.return_value = "This is not JSON at all."
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")
        self.assertEqual(len(res.assignments), 2)

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_response_is_not_a_dict(self, mock_call):
        mock_call.return_value = json.dumps(["an", "array"])
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_missing_assignments_field(self, mock_call):
        mock_call.return_value = json.dumps({"raw_reasoning_summary": "Forgot assignments"})
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_unknown_member_id_in_response(self, mock_call):
        bad_payload = {
            "assignments": [
                {"chore_id": 1, "member_id": 999, "reasoning": "Non-existent member"},
                {"chore_id": 2, "member_id": 2, "reasoning": "Valid member"},
            ],
            "raw_reasoning_summary": "Bad member ID",
        }
        mock_call.return_value = json.dumps(bad_payload)
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")
        for a in res.assignments:
            self.assertIn(a.member_id, [1, 2])

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_unknown_chore_id_in_response(self, mock_call):
        bad_payload = {
            "assignments": [
                {"chore_id": 999, "member_id": 1, "reasoning": "Non-existent chore"},
                {"chore_id": 2, "member_id": 2, "reasoning": "Valid chore"},
            ],
            "raw_reasoning_summary": "Bad chore ID",
        }
        mock_call.return_value = json.dumps(bad_payload)
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_chores_not_all_assigned(self, mock_call):
        incomplete_payload = {
            "assignments": [
                {"chore_id": 1, "member_id": 1, "reasoning": "Chore 1 assigned"},
            ],
            "raw_reasoning_summary": "Forgot chore 2",
        }
        mock_call.return_value = json.dumps(incomplete_payload)
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")
        self.assertEqual(len(res.assignments), 2)

    @patch.object(LLMAllocationEngine, "_call_provider")
    def test_fallback_when_duplicate_chore_assigned(self, mock_call):
        duplicate_payload = {
            "assignments": [
                {"chore_id": 1, "member_id": 1, "reasoning": "Chore 1 to Alice"},
                {"chore_id": 1, "member_id": 2, "reasoning": "Chore 1 to Bob"},
            ],
            "raw_reasoning_summary": "Duplicated chore 1",
        }
        mock_call.return_value = json.dumps(duplicate_payload)
        engine = LLMAllocationEngine(provider="openai", api_key="sk-test")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock (fallback)")

    def test_explicit_mock_provider_returns_mock(self):
        engine = LLMAllocationEngine(provider="mock")
        req = AllocationRequest(members=self.members, chores=self.chores)

        res = engine.allocate(req)
        self.assertEqual(res.engine_used, "mock")
        self.assertEqual(len(res.assignments), 2)


class LLMAllocationEngineProviderNetworkTests(TestCase):
    """Tests verifying HTTP request construction and payload format for each provider."""

    @patch("urllib.request.urlopen")
    def test_call_provider_openai(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": '{"assignments": []}'}}]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        engine = LLMAllocationEngine(provider="openai", api_key="sk-openai-key")
        result = engine._call_provider("Test prompt")

        self.assertEqual(result, '{"assignments": []}')
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(req.headers["Authorization"], "Bearer sk-openai-key")
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertEqual(payload["messages"][1]["content"], "Test prompt")

    @patch("urllib.request.urlopen")
    def test_call_provider_groq(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": '{"assignments": []}'}}]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        engine = LLMAllocationEngine(provider="groq", api_key="gsk-groq-key")
        result = engine._call_provider("Test groq prompt")

        self.assertEqual(result, '{"assignments": []}')
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(req.headers["Authorization"], "Bearer gsk-groq-key")
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "llama-3.3-70b-versatile")

    @patch("urllib.request.urlopen")
    def test_call_provider_gemini(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": '{"assignments": []}'}]}}]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        engine = LLMAllocationEngine(provider="gemini", api_key="gemini-key")
        result = engine._call_provider("Test gemini prompt")

        self.assertEqual(result, '{"assignments": []}')
        req = mock_urlopen.call_args[0][0]
        self.assertIn("generativelanguage.googleapis.com", req.full_url)
        self.assertIn("key=gemini-key", req.full_url)
        payload = json.loads(req.data.decode("utf-8"))
        self.assertIn("Test gemini prompt", payload["contents"][0]["parts"][0]["text"])

    def test_call_provider_unsupported_raises_value_error(self):
        engine = LLMAllocationEngine(provider="unsupported", api_key="test-key")
        with self.assertRaises(ValueError):
            engine._call_provider("prompt")


class LLMAllocationEngineValidationAndEdgeCasesTests(TestCase):
    """Tests verifying edge cases and invalid inputs."""

    def setUp(self):
        self.engine = LLMAllocationEngine(provider="openai", api_key="sk-test")

    def test_invalid_request_type_raises_error(self):
        with self.assertRaises(InvalidAllocationRequestError):
            self.engine.allocate("invalid")  # type: ignore

    def test_empty_members_raises_error(self):
        with self.assertRaises(InvalidAllocationRequestError):
            mock_req = MagicMock(spec=AllocationRequest)
            mock_req.members = []
            self.engine.allocate(mock_req)


class LLMAllocationEngineConfigurationTests(TestCase):
    """Tests verifying configuration resolution from Django settings and environment variables."""

    @override_settings(AI_PROVIDER="groq", GROQ_API_KEY="settings-groq-key")
    def test_resolves_provider_and_key_from_django_settings(self):
        engine = LLMAllocationEngine()
        self.assertEqual(engine.provider, "groq")
        self.assertEqual(engine.api_key, "settings-groq-key")

    def test_resolves_provider_and_key_from_environment(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "env-gemini-key"}):
            with override_settings(AI_PROVIDER=None, GEMINI_API_KEY=None):
                engine = LLMAllocationEngine()
                self.assertEqual(engine.provider, "gemini")
                self.assertEqual(engine.api_key, "env-gemini-key")
