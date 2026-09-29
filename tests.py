import tempfile
import unittest

from pathlib import Path

from fitness import (
    FitnessAnalyzer,
    read_people,
    read_sessions
)


P_HEAD = (
    "participant_id,name,"
    "baseline_heart_rate,"
    "baseline_skin_response,"
    "baseline_temperature\n"
)


S_HEAD = (
    "session_id,participant_id,"
    "timestamp,heart_rate,"
    "skin_response,temperature,"
    "activity_level,signal_quality\n"
)


class TestFitness(unittest.TestCase):

    def test_valid_data(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            p = td / "participants.csv"
            s = td / "sessions.csv"

            p.write_text(
                P_HEAD
                + "P001,Alex,60,1.5,33.0\n",
                encoding="utf-8"
            )

            s.write_text(
                S_HEAD
                + "FIT-2026-001,P001,0,62,1.5,33.0,0.10,0.90\n"
                + "FIT-2026-001,P001,1,64,1.6,33.1,0.12,0.91\n"
                + "FIT-2026-001,P001,2,63,1.5,33.0,0.11,0.92\n",
                encoding="utf-8"
            )

            ppl, pr = read_people(p)

            ses, sr, ok = read_sessions(
                s,
                ppl
            )

            self.assertEqual(
                len(pr),
                0
            )

            self.assertEqual(
                len(sr),
                0
            )

            self.assertEqual(
                ok,
                3
            )

            self.assertEqual(
                len(ses),
                1
            )

            an = FitnessAnalyzer()

            self.assertEqual(
                an.classify(ses[0]),
                "resting"
            )

    def test_invalid_data(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            p = td / "participants.csv"
            s = td / "sessions.csv"

            p.write_text(
                P_HEAD
                + "P001,Alex,60,1.5,33.0\n",
                encoding="utf-8"
            )

            s.write_text(
                S_HEAD
                + "FIT-2026-001,P001,0,fast,1.5,33.0,0.20,0.90\n",
                encoding="utf-8"
            )

            ppl, _ = read_people(p)

            _, rej, ok = read_sessions(
                s,
                ppl
            )

            self.assertEqual(
                ok,
                0
            )

            self.assertEqual(
                len(rej),
                1
            )

            self.assertEqual(
                rej[0]["field"],
                "heart_rate"
            )

    def test_invalid_id(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            p = td / "participants.csv"
            s = td / "sessions.csv"

            p.write_text(
                P_HEAD
                + "P001,Alex,60,1.5,33.0\n",
                encoding="utf-8"
            )

            s.write_text(
                S_HEAD
                + "FIT-26-001,P001,0,70,1.5,33.0,0.20,0.90\n",
                encoding="utf-8"
            )

            ppl, _ = read_people(p)

            _, rej, ok = read_sessions(
                s,
                ppl
            )

            self.assertEqual(
                ok,
                0
            )

            self.assertEqual(
                rej[0]["field"],
                "session_id"
            )

    def test_boundary_values(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            p = td / "participants.csv"
            s = td / "sessions.csv"

            p.write_text(
                P_HEAD
                + "P001,Alex,60,1.5,33.0\n",
                encoding="utf-8"
            )

            s.write_text(
                S_HEAD
                + "FIT-2026-001,P001,0,35,0,25,0,0.60\n"
                + "FIT-2026-001,P001,1,205,0,42,1,1\n"
                + "FIT-2026-001,P001,2,60,1.5,33,0.1,0.9\n",
                encoding="utf-8"
            )

            ppl, _ = read_people(p)

            ses, rej, ok = read_sessions(
                s,
                ppl
            )

            self.assertEqual(
                len(rej),
                0
            )

            self.assertEqual(
                ok,
                3
            )

            self.assertEqual(
                len(ses[0].obs),
                3
            )

    def test_missing_file(self):
        with self.assertRaises(
            FileNotFoundError
        ):
            read_people(
                "file_does_not_exist.csv"
            )


if __name__ == "__main__":
    unittest.main()