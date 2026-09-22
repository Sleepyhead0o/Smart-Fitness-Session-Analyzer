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
        heart_rate,
        skin_response,
        temperature,
        activity_level,
        signal_quality
    ):
        self.timestamp = timestamp
        self.skin_response = skin_response
        self.heart_rate = heart_rate
        self.temperature = temperature
        self.activity_level = activity_level
        self.signal_quality = signal_quality

    @staticmethod
    def is_number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def is_valid(self):
        if not self.is_number(self.heart_rate):
            return False

        if not self.is_number(self.skin_response):
            return False

        if not self.is_number(self.temperature):
            return False

        if not self.is_number(self.activity_level):
            return False

        if not self.is_number(self.signal_quality):
            return False

        if not 30 <= self.heart_rate <= 220:
            return False

        if not 0 <= self.skin_response <= 20:
            return False

        if not 25 <= self.temperature <= 45:
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
                data["heart_rate"],
                data["skin_response"],
                data["temperature"],
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
                f"The average heart rate was {avg_hr:.1f} bpm and the average activity"
                f"level was {avg_act:.2f}. These values were high compared"
                f"with the reference values, which indicates a high activity level"
            )

        if avg_hr >= ref.resting_hr + 20 or avg_act >= 0.35:
            return (
                "Moderate activity level",
                f"The participants average heart rate was {avg_hr:.1f} bpm compared with "
                f"the resting heart rate of {ref.resting_hr} bpm.While the Average "
                f"activity level was {avg_act:.2f}. Both values were above "
                f"resting level, but not high enough for classification of high activity."
            )

        return (
            "Resting",
            f"The participants avg heart rate was {avg_hr:.1f} bpm, and is close to "
            f"their resting heart rate of {ref.resting_hr} bpm. While their average"
            f"activity level was only {avg_act:.2f}."
        )
