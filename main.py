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
