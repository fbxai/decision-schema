"""Run with: uv run --with jsonschema python -B -m unittest discover -s tests -t . -v"""

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "decision.schema.json").read_text())
        cls.validator = Draft202012Validator(cls.schema)

    def setUp(self):
        self.policy = json.loads((ROOT / "examples/decisions.jev.example.json").read_text())
        self.native_policy = json.loads((ROOT / "examples/decisions.example.json").read_text())

    def test_schema_and_examples(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["$id"], "https://github.com/fbxai/decision-schema/decision.schema.json")
        for path in (ROOT / "examples").glob("*.json"):
            with self.subTest(example=path.name):
                policy = json.loads(path.read_text())
                self.validator.validate(policy)
                self.assertEqual(policy["$schema"], self.schema["$id"])

    def test_v1_question_contract(self):
        for field, value in (("version", True), ("version", 2), ("model", "other"),
                             ("endpoint", "https://example.com"), ("questions", []),
                             ("questions", self.native_policy["questions"] * 134)):
            policy = copy.deepcopy(self.native_policy)
            policy[field] = value
            with self.subTest(field=field):
                self.assertFalse(self.validator.is_valid(policy))
        for field, value in (("type", "noul"), ("instructions", " "), ("name", ""),
                             ("choices", [])):
            policy = copy.deepcopy(self.native_policy)
            policy["questions"][0][field] = value
            with self.subTest(field=field):
                self.assertFalse(self.validator.is_valid(policy))

    def test_v1_option_limits_and_types(self):
        for index, field, key, maximum in ((1, "choices", "value", 255), (2, "levels", "label", 10)):
            for count in (1, 2, maximum, maximum + 1):
                policy = copy.deepcopy(self.native_policy)
                policy["questions"][index][field] = [
                    {key: str(i), "description": "Option"} for i in range(count)
                ]
                with self.subTest(field=field, count=count):
                    self.assertEqual(self.validator.is_valid(policy), 2 <= count <= maximum)
            policy = copy.deepcopy(self.native_policy)
            del policy["questions"][index][field][0]["description"]
            self.assertFalse(self.validator.is_valid(policy))
        self.native_policy["questions"][1]["choices"] = [
            {"value": True, "description": "Boolean"},
            {"value": "true", "description": "String"},
        ]
        self.validator.validate(self.native_policy)
        self.native_policy["questions"][1]["choices"][0]["value"] = 1
        self.assertFalse(self.validator.is_valid(self.native_policy))

    def test_structured_content_and_optional_descriptions(self):
        self.policy["questions"]["owner"]["instructions"] = {"question": "Who owns this?", "context": [1, True, None]}
        self.policy["questions"]["owner"]["criteria"]["engineering"] = {"includes": ["crashes"], "excludes": None}
        self.policy["questions"]["owner"]["criteria"]["other"] = None
        self.policy["questions"]["severity"]["criteria"][0] = ["Cosmetic", {"impact": 0}]
        self.policy["questions"]["needs_review"]["criteria"] = {"true": None, "false": None}
        self.validator.validate(self.policy)
        self.policy["questions"]["needs_review"]["instructions"] = None
        self.assertFalse(self.validator.is_valid(self.policy))
        self.policy["questions"]["needs_review"]["criteria"]["true"] = {"condition": "Unresolved"}
        self.validator.validate(self.policy)

    def test_unknown_fields_and_versions(self):
        for field, value in (("version", 3), ("version", True), ("model", "other"), ("endpoint", "https://example.com")):
            policy = copy.deepcopy(self.policy)
            policy[field] = value
            with self.subTest(field=field):
                self.assertFalse(self.validator.is_valid(policy))
        self.policy["questions"]["owner"]["choices"] = []
        self.assertFalse(self.validator.is_valid(self.policy))

    def test_question_types_and_content(self):
        for question in ({"type": "box"}, {"type": "predicate", "instructions": "True?"},
                         {"type": "noul"}, {"type": "noul", "instructions": 123},
                         {"type": "choice", "criteria": {"only": "One"}},
                         {"type": "score", "criteria": ["One"]}):
            with self.subTest(question=question):
                self.assertFalse(self.validator.is_valid({"version": 2, "questions": {"test": question}}))

    def test_container_limits_and_names(self):
        for count in (0, 1, 400, 401):
            questions = {f"q{i}": {"type": "noul", "instructions": "Does this apply?"} for i in range(count)}
            with self.subTest(count=count):
                self.assertEqual(self.validator.is_valid({"version": 2, "questions": questions}), 1 <= count <= 400)
        self.policy["questions"][" "] = {"type": "noul", "instructions": "True?"}
        self.assertFalse(self.validator.is_valid(self.policy))

    def test_option_limits(self):
        for count in (1, 2, 255, 256):
            question = {"type": "choice", "criteria": {f"o{i}": None for i in range(count)}}
            with self.subTest(kind="choice", count=count):
                self.assertEqual(self.validator.is_valid({"version": 2, "questions": {"test": question}}), 2 <= count <= 255)
        for count in (1, 2, 10, 11):
            question = {"type": "score", "criteria": ["Level"] * count}
            with self.subTest(kind="score", count=count):
                self.assertEqual(self.validator.is_valid({"version": 2, "questions": {"test": question}}), 2 <= count <= 10)


if __name__ == "__main__":
    unittest.main()
