# After the csv data files has been read and validated, this file analyses the data. 

from statistics import mean


def avg(v):     # v values 
    if not v:
        return 0.0

    return mean(v)


def stats(v):
    return {
        "avg": avg(v),
        "min": min(v),
        "max": max(v)
    }
"""
# Calculates how much a value decrease at the start of a session compared with the end.
# Example: If drop() returns a large positive value, it means that the heart rate have fallen.
def drop(v):
    if len(v) < 6:
        return 0.0

    n = max(
        2,
        len(v) // 3
    )

    a = avg(v[:n])
    b = avg(v[-n:])

    return a - b 
    """
# Calculates how much a value decreases from the active part to the end.
def drop(v):
    if len(v) < 6:
        return 0.0

    n = max(
        2,
        len(v) // 3
    )

    a = avg(v[n:-n])
    b = avg(v[-n:])

    return a - b

# classify a session as resting, moderate activity and high activity
class ActivityAnalysis:
    def classify(self, s):
        hr = [
            o.hr
            for o in s.obs
        ]

        ac = [          # activity values
            o.act
            for o in s.obs
        ]

        dhr = avg(hr) - s.p.ref.hr      # dhr heart rate difference

        if avg(ac) >= 0.67 or dhr >= 45:
            return "high activity"

        if avg(ac) >= 0.30 or dhr >= 15:
            return "moderate activity"

        return "resting"

# Detects recovery: checks if hr and act decrease enough to indicate recovery
class RecoveryAnalysis:
    def check(self, s):
        if len(s.obs) < 6:
            return False

        hr = [
            o.hr
            for o in s.obs
        ]

        ac = [
            o.act
            for o in s.obs
        ]

        return (
            drop(hr) >= 20
            and drop(ac) >= 0.20
        )


class FitnessAnalyzer:
    def __init__(self):
        self.act = ActivityAnalysis()
        self.rec = RecoveryAnalysis()

    def classify(self, s):
        n = len(s.obs)

        if n < 3:
            return "insufficient data"

        if s.total == 0:
            return "insufficient data"

        if n / s.total < 0.50:
            return "insufficient data"

        if self.rec.check(s):
            return "recovering"

        return self.act.classify(s)

    def analyze(self, s):
        c = self.classify(s)

        r = {
            "session_id": s.sid,
            "participant_id": s.p.pid,
            "participant_name": s.p.name,
            "classification": c,
            "usable": len(s.obs),
            "total": s.total,
            "rejected": s.total - len(s.obs),
            "summary": {},
            "explanation": ""
        }

        if not s.obs:
            r["explanation"] = (
                "There are no usable observations "
                "to classify the session."
            )

            return r

        r["summary"] = {
            "heart_rate": stats(
                [o.hr for o in s.obs]
            ),
            "skin_response": stats(
                [o.sk for o in s.obs]
            ),
            "temperature": stats(
                [o.tp for o in s.obs]
            ),
            "activity_level": stats(
                [o.act for o in s.obs]
            ),
            "signal_quality": stats(
                [o.q for o in s.obs]
            )
        }

        hr = r["summary"]["heart_rate"]["avg"]
        sk = r["summary"]["skin_response"]["avg"]
        tp = r["summary"]["temperature"]["avg"]
        ac = r["summary"]["activity_level"]["avg"]

        dhr = hr - s.p.ref.hr
        dsk = sk - s.p.ref.sk
        dtp = tp - s.p.ref.tp

        if c == "recovering":
            txt = (
                "Heart rate and activity decrease near "
                "the end of the session. "
                f"Average heart rate is {dhr:.1f} bpm "
                "above baseline."
            )

        elif c == "high activity":
            txt = (
                f"Average activity is {ac:.2f} and "
                f"heart rate is {dhr:.1f} bpm above baseline. "
                f"Skin response differs by {dsk:.2f} and "
                f"temperature by {dtp:.2f} °C."
            )

        elif c == "moderate activity":
            txt = (
                f"Average activity is {ac:.2f} and "
                f"heart rate is {dhr:.1f} bpm above baseline. "
                f"Skin response differs by {dsk:.2f} and "
                f"temperature by {dtp:.2f} °C."
            )

        elif c == "resting":
            txt = (
                f"Average activity is low at {ac:.2f}. "
                f"Heart rate is {hr:.1f} bpm compared "
                f"with the baseline of {s.p.ref.hr} bpm."
            )

        else:
            txt = (
                f"Only {len(s.obs)} of {s.total} "
                "observations are usable. "
                "There are too few usable observations "
                "to classify the session."
            )

        r["explanation"] = txt

        return r