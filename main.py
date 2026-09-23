from statistics import mean
from data_generator import available_scenarios, generate_fitness_data


class Ref:
    def __init__(self, hr, sk, tp):
        self.hr = hr
        self.sk = sk
        self.tp = tp

    @property
    def hr(self):
        return self.__hr

    @hr.setter
    def hr(self, v):
        if not isinstance(v, (int, float)) or v <= 0:
            raise ValueError("Invalid baseline heart rate")

        self.__hr = v


class Person:
    def __init__(self, pid, ref):
        self.pid = pid
        self.ref = ref

# One Observation
class Obs:
    def __init__(self, t, hr, sk, tp, act, q):
        self.t = t
        self.hr = hr
        self.sk = sk
        self.tp = tp
        self.act = act
        self.q = q

        self.ok, self.err = self.validate()

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get("timestamp"),
            d.get("heart_rate"),
            d.get("skin_response"),
            d.get("temperature"),
            d.get("activity_level"),
            d.get("signal_quality")
        )

    def validate(self):
        if not isinstance(self.t, int) or self.t < 0:
            return False, "Invalid timestamp. A timestamp must be an integer with a number greater than or equal to 0"

        if (
            not isinstance(self.hr, (int, float))
            or not 35 <= self.hr <= 205
        ):
            return False, "Invalid heart rate. It have to be a number between 35 and 205."

        if (
            not isinstance(self.sk, (int, float))
            or self.sk < 0
        ):
            return False, "Invalid skin response. It have to be a number and cannot be negative."

        if (
            not isinstance(self.tp, (int, float))
            or not 25 <= self.tp <= 42
        ):
            return False, "Invalid temperature. It have to be a number between 25 and 42."

        if (
            not isinstance(self.act, (int, float))
            or not 0 <= self.act <= 1
        ):
            return False, "Invalid activity level. It have to be a number between 0 and 1."

        if (
            not isinstance(self.q, (int, float))
            or not 0 <= self.q <= 1
        ):
            return False, "Invalid signal quality. It have to be a number between 0 and 1."

        if self.q < 0.60:
            return False, "Poor signal quality. The value must be 0.60 or higher."

        return True, ""

# Multiple observations
class Session:
    def __init__(self, p, obs, sc):
        self.p = p
        self.obs = obs
        self.sc = sc

    @property
    def good(self):
        return [o for o in self.obs if o.ok]


class Analyzer:
    def classify(self, s):
        raise NotImplementedError

# FitnessAnalyzer inherits from Analyzer. Method overriding
class FitnessAnalyzer(Analyzer):
    def classify(self, s):
        g = s.good

        if len(g) < 3:
            return "insufficient data"

        if len(g) / len(s.obs) < 0.50:
            return "insufficient data"

        hr = [o.hr for o in g]
        ac = [o.act for o in g]

        dhr = avg(hr) - s.p.ref.hr

        if drop(hr) >= 20 and drop(ac) >= 0.20:
            return "recovering"

        if avg(ac) >= 0.67 or dhr >= 45:
            return "high activity"

        if avg(ac) >= 0.30 or dhr >= 15:
            return "moderate activity"

        return "resting"

    def analyze(self, s):
        g = s.good
        c = self.classify(s)

        r = {
            "participant": s.p.pid,
            "scenario": s.sc,
            "classification": c,
            "usable": len(g),
            "total": len(s.obs),
            "rejected": len(s.obs) - len(g),
            "summary": {},
            "explanation": ""
        }

        if not g:
            r["explanation"] = (
                "There are too few usable observations "
                "to classify the session."
            )
            return r

        r["summary"] = {
            "heart_rate": stats(
                [o.hr for o in g]
            ),
            "skin_response": stats(
                [o.sk for o in g]
            ),
            "temperature": stats(
                [o.tp for o in g]
            ),
            "activity_level": stats(
                [o.act for o in g]
            ),
            "signal_quality": stats(
                [o.q for o in g]
            )
        }

        hr = r["summary"]["heart_rate"]["avg"]
        ac = r["summary"]["activity_level"]["avg"]

        dhr = hr - s.p.ref.hr

        if c == "recovering":
            txt = (
                "Heart rate and activity decrease near the "
                "end of the session. "
                f"Average heart rate is {dhr:.1f} bpm "
                "above the participant's baseline."
            )

        elif c == "high activity":
            txt = (
                f"Average activity level is {ac:.2f} and "
                f"heart rate is {dhr:.1f} bpm above baseline."
            )

        elif c == "moderate activity":
            txt = (
                f"Average activity level is {ac:.2f} and "
                f"heart rate is {dhr:.1f} bpm above baseline."
            )

        elif c == "resting":
            txt = (
                "Activity is low and heart rate is close "
                f"to the baseline of {s.p.ref.hr} bpm."
            )

        else:
            txt = (
                "There are too few usable observations "
                "to classify the session."
            )

        r["explanation"] = txt

        return r


def avg(v):
    if not v:
        return 0.0

    return mean(v)


def stats(v):
    return {
        "avg": avg(v),
        "min": min(v),
        "max": max(v)
    }


def drop(v):
    if len(v) < 6:
        return 0.0

    n = max(2, len(v) // 3)

    a = avg(v[:n])
    b = avg(v[-n:])

    return a - b


def build_session(pd, od, sc):
    ref = Ref(
        pd["baseline_heart_rate"],
        pd["baseline_skin_response"],
        pd["baseline_temperature"]
    )

    p = Person(
        pd["participant_id"],
        ref
    )

    obs = [
        Obs.from_dict(d)
        for d in od
    ]

    return Session(
        p,
        obs,
        sc
    )


def print_report(r):
    print("\n" + "=" * 58)

    print("Scenario:", r["scenario"])
    print("Participant:", r["participant"])
    print(
        "Usable observations:",
        str(r["usable"]) + "/" + str(r["total"])
    )
    print("Classification:", r["classification"])

    if r["summary"]:
        print()
        print(
            f"{'Measurement':<20}"
            f"{'Average':>10}"
            f"{'Minimum':>10}"
            f"{'Maximum':>10}"
        )

        print("-" * 50)

        names = {
            "heart_rate": "Heart rate",
            "skin_response": "Skin response",
            "temperature": "Temperature",
            "activity_level": "Activity level",
            "signal_quality": "Signal quality"
        }

        for k, n in names.items():
            x = r["summary"][k]

            print(
                f"{n:<20}"
                f"{x['avg']:>10.2f}"
                f"{x['min']:>10.2f}"
                f"{x['max']:>10.2f}"
            )

    print()
    print("Explanation:")
    print(r["explanation"])


def main():
    a = FitnessAnalyzer()

    for sc in available_scenarios():

        pd, od = generate_fitness_data(
            participant_id="P001",
            scenario=sc,
            seed=49,
            number_of_windows=12
        )

        s = build_session(
            pd,
            od,
            sc
        )

        r = a.analyze(s)

        print_report(r)


if __name__ == "__main__":
    main()