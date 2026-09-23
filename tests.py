import unittest

from data_generator import generate_fitness_data

from main import (
    Ref,
    Obs,
    FitnessAnalyzer,
    build_session
)


class TestFitness(unittest.TestCase):

    def test_resting(self):
        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario="resting",
            seed=42,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            "resting"
        )

        a = FitnessAnalyzer()

        self.assertEqual(
            a.classify(s),
            "resting"
        )

    def test_moderate(self):
        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario="moderate_activity",
            seed=42,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            "moderate_activity"
        )

        a = FitnessAnalyzer()

        self.assertEqual(
            a.classify(s),
            "moderate activity"
        )

    def test_high(self):
        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario="high_activity",
            seed=42,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            "high_activity"
        )

        a = FitnessAnalyzer()

        self.assertEqual(
            a.classify(s),
            "high activity"
        )

    def test_recovery(self):
        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario="recovery",
            seed=42,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            "recovery"
        )

        a = FitnessAnalyzer()

        self.assertEqual(
            a.classify(s),
            "recovering"
        )

    def test_poor_quality(self):
        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario="poor_quality",
            seed=42,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            "poor_quality"
        )

        a = FitnessAnalyzer()

        self.assertEqual(
            a.classify(s),
            "insufficient data"
        )

    def test_invalid_hr(self):
        d = {
            "timestamp": 0,
            "heart_rate": 265,
            "skin_response": 1.5,
            "temperature": 32.5,
            "activity_level": 0.5,
            "signal_quality": 0.9
        }

        o = Obs.from_dict(d)

        self.assertFalse(o.ok)

    def test_private_hr(self):
        with self.assertRaises(ValueError):
            Ref(
                -10,
                1.5,
                32.5
            )


if __name__ == "__main__":
    unittest.main()