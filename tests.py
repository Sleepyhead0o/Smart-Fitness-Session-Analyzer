import unittest

from main import (
    ReferenceProfile,
    Member,
    Observation,
    FitnessSession
)

from sample_data import SCENARIOS


class TestFitnessAnalyzer(unittest.TestCase):

    def setUp(self):
        profile = ReferenceProfile(
            resting_hr=65,
            normal_temp=32.8,
            normal_skin=1.5
        )

        self.member = Member(
            "Test member",
            profile
        )

    def get_result(self, name):
        data = SCENARIOS[name]

        obs = [
            Observation.from_dict(item)
            for item in data
        ]

        session = FitnessSession(
            self.member,
            obs
        )

        return session.analyze()

    def test_resting(self):
        result = self.get_result(
            "Resting session"
        )

        self.assertEqual(
            result["classification"],
            "Resting"
        )

    def test_moderate(self):
        result = self.get_result(
            "Moderate activity"
        )

        self.assertEqual(
            result["classification"],
            "Moderate activity"
        )

    def test_high(self):
        result = self.get_result(
            "High activity"
        )

        self.assertEqual(
            result["classification"],
            "High activity"
        )

    def test_recovery(self):
        result = self.get_result(
            "Recovery session"
        )

        self.assertEqual(
            result["classification"],
            "Recovering"
        )

    def test_bad_data(self):
        result = self.get_result(
            "Poor sensor data"
        )

        self.assertEqual(
            result["classification"],
            "Insufficient data"
        )


if __name__ == "__main__":
    unittest.main()