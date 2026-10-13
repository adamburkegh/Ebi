"""Tests of the Python API. Build the extension into the ebi-pm environment first: maturin develop"""
import unittest
from collections import deque
from fractions import Fraction
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


SPACED_LABELS_MODEL = """finite stochastic language
# number of traces
1
# trace 0
# probability
1
# number of events
2
Send Fine
Create Fine
"""


class ProbabilityTrace(unittest.TestCase):
    def setUp(self):
        self.model = (TESTFILES / "aa-ab-ba.slang").read_text()

    def test_probability_of_a_trace_given_as_a_list(self):
        self.assertEqual(ebi.probability_trace(self.model, ["b", "a"]), Fraction(3, 5))

    def test_a_trace_that_is_not_in_the_model_has_probability_zero(self):
        self.assertEqual(ebi.probability_trace(self.model, ["b", "b"]), Fraction(0))

    def test_an_unknown_activity_has_probability_zero(self):
        self.assertEqual(ebi.probability_trace(self.model, ["a", "unknown"]), Fraction(0))

    def test_an_activity_label_may_contain_spaces(self):
        result = ebi.probability_trace(SPACED_LABELS_MODEL, ["Send Fine", "Create Fine"])
        self.assertEqual(result, Fraction(1))

    def test_a_trace_given_as_a_tuple_is_accepted(self):
        self.assertEqual(ebi.probability_trace(self.model, ("b", "a")), Fraction(3, 5))

    def test_a_single_string_is_rejected_instead_of_being_taken_as_one_activity(self):
        with self.assertRaises(ValueError):
            ebi.probability_trace(self.model, "b a")

    def test_any_sequence_of_strings_is_accepted(self):
        trace = deque(["b", "a"])
        self.assertEqual(
            ebi.probability_trace(self.model, trace), Fraction(3, 5)
        )

    def test_a_set_is_rejected_because_it_has_no_order(self):
        with self.assertRaises(ValueError):
            ebi.probability_trace(self.model, {"a", "b"})

    def test_a_generator_is_rejected(self):
        with self.assertRaises(ValueError):
            ebi.probability_trace(self.model, (x for x in ["b", "a"]))

    def test_an_element_that_is_not_a_string_is_rejected(self):
        with self.assertRaises(ValueError):
            ebi.probability_trace(self.model, ["b", 1])


class ModelHandles(unittest.TestCase):
    def setUp(self):
        self.text = (TESTFILES / "aa-ab-ba_occ.slpn").read_text()
        self.model = ebi.Model.from_text(self.text)

    def test_a_model_gives_the_same_answers_as_its_text(self):
        for trace in (["a", "a"], ["b", "a"], ["b", "b"]):
            self.assertEqual(
                ebi.probability_trace(self.model, trace), ebi.probability_trace(self.text, trace)
            )

    def test_a_model_can_be_used_where_the_command_needs_another_kind_of_input(self):
        self.assertEqual(
            ebi.probability_explain_trace(self.model, 0.5, ["a", "a"]),
            ebi.probability_explain_trace(self.text, 0.5, ["a", "a"]),
        )

    def test_a_model_can_be_written_as_text_and_loaded_again(self):
        again = ebi.Model.from_text(self.model.to_text())
        self.assertEqual(
            ebi.probability_trace(again, ["b", "a"]), ebi.probability_trace(self.text, ["b", "a"])
        )

    def test_a_model_knows_what_it_is(self):
        self.assertIn("Petri net", self.model.object_type)

    def test_text_that_is_not_a_model_is_rejected(self):
        with self.assertRaises(ValueError):
            ebi.Model.from_text("this is not a model")

    def test_a_model_is_not_taken_for_a_trace(self):
        with self.assertRaises(ValueError):
            ebi.probability_trace(self.text, self.model)


class FractionResults(unittest.TestCase):
    def setUp(self):
        model = (TESTFILES / "aa-ab-ba.slang").read_text()
        self.result = ebi.probability_trace(model, ["b", "a"])

    def test_a_fraction_is_a_python_fraction(self):
        self.assertIsInstance(self.result, Fraction)
        self.assertEqual((self.result.numerator, self.result.denominator), (3, 5))
        self.assertEqual(float(self.result), 0.6)

    def test_a_negative_fraction_keeps_its_sign_in_every_form(self):
        negative = ebi.EbiFraction(-3, 5)
        self.assertEqual(negative, Fraction(-3, 5))
        self.assertEqual(float(negative), -0.6)
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(list(negative), [-0.6, -3, 5])

    def test_other_fraction_results_are_python_fractions_too(self):
        model = (TESTFILES / "aa-ab-ba_ali.slpn").read_text()
        language = (TESTFILES / "aa.lang").read_text()
        self.assertEqual(ebi.probability_log(model, language), Fraction(0))

    def test_indexing_still_gives_the_old_float_numerator_denominator_but_is_deprecated(self):
        for index, expected in enumerate([0.6, 3, 5]):
            with self.assertWarns(DeprecationWarning):
                self.assertEqual(self.result[index], expected)
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(list(self.result), [0.6, 3, 5])


if __name__ == "__main__":
    unittest.main()
