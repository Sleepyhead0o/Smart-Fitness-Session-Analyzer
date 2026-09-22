class ReferenceProfile:
    def __init__(self, resting_hr, normal_temp, normal_skin):
        self.normal_temp = normal_temp
        self.resting_hr = resting_hr
        self.normal_skin = normal_skin

    @property
    def resting_hr(self):
        return self.__resting_hr

    @resting_hr.setter
    def resting_hr(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("A resting heart rate has to be a positive number.")

        self.__resting_hr = value

# participant
class Member:
    def __init__(self, name, profile):
        self.name = name
        self.profile = profile

class Observation:
    def __init__(
        self,
        timestamp,
        heart_Rate,
        skin_response,
        temp,
        activity_level,
        signal_quality
    ):
        self.timestamp = timestamp
        self.skin_response = skin_response
        self.heart_Rate = heart_Rate
        self.temp = temp
        self.activity_level = activity_level
        self.signal_quality = signal_quality

    @staticmethod
    def is_number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def is_valid(self):
        if not self.is_number(self.heart_Rate):
            return False

        if not self.is_number(self.skin_response):
            return False

        if not self.is_number(self.temp):
            return False

        if not self.is_number(self.activity_level):
            return False

        if not self.is_number(self.signal_quality):
            return False

        if not 30 <= self.heart_Rate <= 220:
            return False

        if not 0 <= self.skin_response <= 20:
            return False

        if not 25 <= self.temp <= 45:
            return False

        if not 0 <= self.activity_level <= 1:
            return False

        if not 0 <= self.signal_quality <= 1:
            return False

        return True

    def is_usable(self):
        return self.is_valid() and self.signal_quality >= 0.50

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                data["timestamp"],
                data["heart_Rate"],
                data["skin_response"],
                data["temp"],
                data["activity_level"],
                data["signal_quality"]
            )

        except KeyError:
            return None

class Session:
    def __init__(self, member, observations):
        self.member = member
        self.observations = observations

    def classify(self, usable, summaries):
        return "Unclassified", "The session was not classified."


class FitnessSession(Session):

    def classify(self, usable, summaries):
        if len(usable) < 3:
            return (
                "Insufficient data",
                "There were fewer than 3 usable observations."
            )

        ref = self.member.profile

        avg_hr = summaries["Heart rate"]["average"]
        avg_act = summaries["Activity level"]["average"]

        if detect_recovery(usable, ref):
            return (
                "Recovering",
                "Heart rate and activity level decreased near the end "
                "of the session after being elevated earlier."
            )

        if avg_hr >= ref.resting_hr + 60 or avg_act >= 0.75:
            return (
                "High activity",
                f"The participant have a average heart rate of {avg_hr:.1f} bpm compared with "
                f"the resting heart rate of {ref.resting_hr} bpm.While the Average "
                f"activity level was {avg_act:.2f}. These values were high compared"
                f"with the reference values, which indicates a high activity level"
            )

        if avg_hr >= ref.resting_hr + 20 or avg_act >= 0.35:
            return (
                "Moderate activity level",
                f"The participant have a average heart rate of {avg_hr:.1f} bpm compared with "
                f"the resting heart rate of {ref.resting_hr} bpm.While the Average "
                f"activity level was {avg_act:.2f}. Both values were above "
                f"resting level, but not high enough for classification of high activity."
            )

        return (
            "Resting",
            f"The participant have a average heart rate of {avg_hr:.1f} bpm, and that is "
            f"close to their resting heart rate of {ref.resting_hr} bpm. While their average"
            f"activity level was only {avg_act:.2f}."
        )

def analyze(self):
        usable = []

        for obs in self.observations:
            if obs is not None and obs.is_usable():
                usable.append(obs)

        summaries = {}

        if len(usable) > 0:
            heart_rates = []
            skin_values = []
            temperatures = []
            activity_values = []
            quality_values = []

            for obs in usable:
                heart_rates.append(obs.heart_Rate)
                skin_values.append(obs.skin_response)
                temperatures.append(obs.temp)
                activity_values.append(obs.activity_level)
                quality_values.append(obs.signal_quality)

            summaries["Heart rate"] = make_summary(heart_rates)
            summaries["Skin response"] = make_summary(skin_values)
            summaries["Temperature"] = make_summary(temperatures)
            summaries["Activity level"] = make_summary(activity_values)
            summaries["Signal quality"] = make_summary(quality_values)

        classification, reason = self.classify(
            usable,
            summaries
        )

        return {
            "member": self.member.name,
            "classification": classification,
            "reason": reason,
            "usable": len(usable),
            "total": len(self.observations),
            "summaries": summaries
        }


def average(values):
    return mean(values)


def make_summary(values):
    return {
        "average": average(values),
        "minimum": min(values),
        "maximum": max(values)
    }


def detect_recovery(observations, ref):
    if len(observations) < 4:
        return False

    heart_rates = []
    activity = []

    for obs in observations:
        heart_rates.append(obs.heart_Rate)
        activity.append(obs.activity_level)

    peak_act = max(activity)
    peak_hr = max(heart_rates)

    last_hr = [
        observations[-2].heart_Rate,
        observations[-1].heart_Rate
    ]

    last_act = [
        observations[-2].activity_level,
        observations[-1].activity_level
    ]

    end_hr = average(last_hr)
    end_act = average(last_act)

    return (
        peak_hr >= ref.resting_hr + 40
        and end_hr <= peak_hr - 20
        and end_act <= peak_act - 0.20
    )

def print_report(result):
    print(
        f"\nThe participant is {result['member']} and this session has "
        f"{result['classification'].lower()}. It has {result['usable']} of {result['total']}"
        f"usable observations.\n"
    )

    if result["summaries"]:
        print(
            f"{'Measurement':<18}"
            f"{'Average':>10}"
            f"{'Minimum':>10}"
            f"{'Maximum':>10}"
        )

        for name, values in result["summaries"].items():
            print(
                f"{name:<18}"
                f"{values['average']:>10.2f}"
                f"{values['minimum']:>10.2f}"
                f"{values['maximum']:>10.2f}"
            )

    else:
        print("There are no usable measurements to summarize.")

    print(
        f"\nExplanation:\n"
        f"{result['reason']}"
    )


def run_scenario(data):
    profile = ReferenceProfile(
        resting_hr=65,
        normal_temp=32.8,
        normal_skin=1.5
    )

    member = Member(
        "Alex",
        profile
    )

    observations = []

    for item in data:
        obs = Observation.from_dict(item)
        observations.append(obs)

    session = FitnessSession(
        member,
        observations
    )

    result = session.analyze()

    print_report(result)


if __name__ == "__main__":
    for name, data in SCENARIOS.items():
        print(f"\n--- {name} ---")
        run_scenario(data)