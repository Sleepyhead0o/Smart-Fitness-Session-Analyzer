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