import argparse
import csv
from pathlib import Path

from fitness import (
    FitnessAnalyzer,
    InvalidRecordError,
    read_people,
    read_sessions,
    save_reports
)


def args():
    p = argparse.ArgumentParser(   # parser
        description="Smart Fitness Session Analyzer"
    )

    p.add_argument(
        "--profiles",
        default="data/participants.csv"
    )

    p.add_argument(
        "--sessions",
        nargs="+",
        default=[
            "data/fitness_sessions.csv",
            "data/fitness_sessions_invalid.csv"
        ]
    )

    p.add_argument(
        "--output",
        default="output"
    )

    return p.parse_args()


def main():
    a = args()

    rej = []        # rejected records
    ses = []        # sessions
    ok = 0          # number of approved rows 

    try:
        ppl, r = read_people(a.profiles)    # ppl participants/people
        rej.extend(r)       # r rejected rows

    except FileNotFoundError:
        print("Profile file not found:", a.profiles)
        return

    except PermissionError:
        print("No permission to read:", a.profiles)
        return

    except (InvalidRecordError, csv.Error) as e:
        print("Could not read profile file:", e)
        return

    for src in a.sessions:

        try:
            s, r, n = read_sessions(
                src,
                ppl
            )

            ses.extend(s)
            rej.extend(r)
            ok += n

        except FileNotFoundError:
            rej.append({
                "source": Path(src).name,
                "row": 0,
                "field": "file",
                "reason": "File not found."
            })

        except PermissionError:
            rej.append({
                "source": Path(src).name,
                "row": 0,
                "field": "file",
                "reason": "Permission denied."
            })

        except (InvalidRecordError, csv.Error) as e:
            rej.append({
                "source": Path(src).name,
                "row": 0,
                "field": "file",
                "reason": str(e)
            })

    an = FitnessAnalyzer()

    res = [
        an.analyze(s)
        for s in ses
    ]

    files = save_reports(
        a.output,
        res,
        rej
    )

    print("Analysis complete.")
    print("Accepted rows:", ok)
    print("Rejected rows:", len(rej))
    print("Processed sessions:", len(res))

    print("Created files:")

    for f in files:
        print("-", f)


if __name__ == "__main__":
    main()