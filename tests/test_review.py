import unittest

from redteam.review import make_template


class ReviewTests(unittest.TestCase):
    def test_pending_template(self):
        template = make_template({"results": [{"id": "B1", "kind": "benign"},
                                              {"id": "T2", "kind": "attack"}]})
        self.assertEqual(len(template["reviews"]), 2)
        self.assertTrue(all(x["review_status"] == "pending" for x in template["reviews"]))
        self.assertEqual(template["reviews"][1]["instruction_boundary"], "uncertain")

    def test_missing_results(self):
        with self.assertRaises(ValueError):
            make_template({})
