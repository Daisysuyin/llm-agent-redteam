import unittest
from redteam.multimodel import capability, compare


class FakeAdapter:
    def __init__(self, name="add_numbers", arguments=None):
        self.name = name
        self.arguments = {"a": 17, "b": 25} if arguments is None else arguments

    def decide(self, messages, tools):
        return {"message": {"tool_calls": [{"function": {
            "name": self.name, "arguments": self.arguments}}]}}


class MultiModelTests(unittest.TestCase):
    def test_valid_structured_call(self):
        score = capability(FakeAdapter())
        self.assertTrue(score["correct_tool_selected"])
        self.assertTrue(score["correct_arguments"])

    def test_correct_tool_wrong_arguments(self):
        score = capability(FakeAdapter(arguments={"a": 18, "b": 25}))
        self.assertTrue(score["correct_tool_selected"])
        self.assertFalse(score["correct_arguments"])

    def test_string_json_arguments(self):
        score = capability(FakeAdapter(arguments='{"a":17,"b":25}'))
        self.assertTrue(score["correct_arguments"])

    def test_bool_not_integer(self):
        score = capability(FakeAdapter(arguments={"a": True, "b": 25}))
        self.assertFalse(score["correct_arguments"])

    def test_wrong_tool(self):
        score = capability(FakeAdapter(name="wrong_tool"))
        self.assertFalse(score["correct_tool_selected"])

    def test_different_model_error_preserved(self):
        def factory(name):
            if name == "unavailable":
                raise RuntimeError("model unavailable")
            return FakeAdapter()
        result = compare(["model1", "unavailable"], factory, capability_only=True)
        self.assertEqual(len(result["results"]), 2)
        self.assertTrue(result["results"][0]["capability"]["correct_arguments"])
        self.assertEqual(result["results"][1]["error_type"], "RuntimeError")

    def test_duplicate_models_rejected(self):
        with self.assertRaises(ValueError):
            compare(["a", "a"], lambda x: FakeAdapter(), True)
