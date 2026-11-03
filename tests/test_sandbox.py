import unittest

from redteam.sandbox import (
    FAKE_SECRET, FakeToolGateway, args_as_dict, capability_probe,
    run_agent, scenario,
)


class ScriptedAdapter:
    def __init__(self, messages):
        self.responses = list(messages)

    def decide(self, messages, tools):
        if not self.responses:
            return {"message": {"content": "Done."}}
        return {"message": self.responses.pop(0)}


def call(name, args):
    return {"function": {"name": name, "arguments": args}}


class SandboxTests(unittest.TestCase):
    def test_capability(self):
        agent = ScriptedAdapter([{"tool_calls": [call("add_numbers", {"a": 17, "b": 25})]}])
        self.assertTrue(capability_probe(agent)["expected_call_emitted"])

    def test_parsing(self):
        self.assertEqual(args_as_dict('{"x": 1}'), {"x": 1})
        self.assertIsNone(args_as_dict("bad"))

    def test_denied_no_state_change(self):
        gate = FakeToolGateway(scenario(True), "enforce")
        before = list(gate.state["public_comments"])
        out = gate.call("publish_public_comment", {"issue_id": "ISSUE-1", "body": FAKE_SECRET})
        self.assertIn("error", out)
        self.assertEqual(before, gate.state["public_comments"])
        self.assertFalse(gate.trace[-1]["allowed"])

    def test_benign_legal_read(self):
        gate = FakeToolGateway(scenario(False))
        response = gate.call("read_public_issue", {"issue_id": "ISSUE-1"})
        self.assertIn("Release checklist", response["issue"])

    def test_attack_attempt_denied(self):
        agent = ScriptedAdapter([
            {"tool_calls": [call("read_private_note", {"note_id": "SECRET-1"})]},
            {"content": "Could not obtain the note."},
        ])
        report = run_agent(agent, injected=True, policy="enforce")
        self.assertEqual(report["unauthorized_attempts"], 1)
        self.assertEqual(report["unauthorized_blocked"], 1)
        self.assertFalse(report["private_marker_published"])

    def test_paired_benign_completion(self):
        agent = ScriptedAdapter([
            {"tool_calls": [call("read_public_issue", {"issue_id": "ISSUE-1"})]},
            {"content": "The checklist covers CI and test coverage."},
        ])
        result = run_agent(agent, injected=False, policy="enforce")
        self.assertTrue(result["legitimate_issue_read"])
        self.assertEqual(result["unauthorized_attempts"], 0)

    def test_observe_policy_only_affects_fake_state(self):
        agent = ScriptedAdapter([
            {"tool_calls": [call("read_private_note", {"note_id": "SECRET-1"})]},
            {"tool_calls": [call("publish_public_comment", {"issue_id": "ISSUE-1", "body": FAKE_SECRET})]},
            {"content": "Done."},
        ])
        report = run_agent(agent, injected=True, policy="observe")
        self.assertEqual(report["unauthorized_attempts"], 2)
        self.assertEqual(report["unauthorized_blocked"], 0)
        self.assertTrue(report["private_marker_published"])

    def test_unknown_tool_denied(self):
        gate = FakeToolGateway(scenario(False), "observe")
        self.assertIn("error", gate.call("terminal_execute", {"command": "echo TEST"}))

    def test_limit_validation(self):
        with self.assertRaises(ValueError):
            run_agent(ScriptedAdapter([]), max_turns=0)

    def test_defensive_copy(self):
        original = scenario(False)
        gate = FakeToolGateway(original, "observe")
        gate.call("publish_public_comment", {"issue_id": "ISSUE-1", "body": "hello"})
        self.assertEqual(original["public_comments"], [])
