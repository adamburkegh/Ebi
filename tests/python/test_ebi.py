"""Tests of the Python API. Build the extension into the ebi-pm environment first: maturin develop"""
import unittest
from pathlib import Path

import ebi

TESTFILES = Path(__file__).resolve().parents[2] / "testfiles"


class ExposedFunctions(unittest.TestCase):
    def test_withheld_functions_are_absent(self):
        for name in ("reduce_process_tree", "discover_non_stochastic_split_miner"):
            self.assertFalse(hasattr(ebi, name), name)


class ConvertStochasticDirectlyFollowsModel(unittest.TestCase):
    def test_converts_a_model_given_as_text(self):
        model = (TESTFILES / "aa-ab-ba.sdfm").read_text()
        result = ebi.convert_stochastic_directly_follows_model(model)
        self.assertTrue(result.startswith("stochastic directly follows model"))


if __name__ == "__main__":
    unittest.main()
