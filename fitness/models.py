
# reference values
class Ref:
    def __init__(self, hr, sk, tp):
        self.hr = hr        # heart rate
        self.sk = sk        # skin response
        self.tp = tp        # temperature

    # property is used to control the values before they are stored
    @property
    def hr(self):
        return self.__hr

    @hr.setter
    def hr(self, v):
        if not isinstance(v, (int, float)) or not 35 <= v <= 205:
            raise ValueError(
                "Baseline heart rate must be between 35 and 205."
            )

        self.__hr = v

    @property
    def sk(self):
        return self.__sk

    @sk.setter
    def sk(self, v):
        if not isinstance(v, (int, float)) or v < 0:
            raise ValueError(
                "Baseline skin response cannot be negative."
            )

        self.__sk = v

    @property
    def tp(self):
        return self.__tp

    @tp.setter
    def tp(self, v):
        if not isinstance(v, (int, float)) or not 25 <= v <= 42:
            raise ValueError(
                "Baseline temperature must be between 25 and 42."
            )

        self.__tp = v

# participant
class Person:
    def __init__(self, pid, name, ref):
        self.pid = pid
        self.name = name
        self.ref = ref

# observation
class Obs:
    def __init__(self, t, hr, sk, tp, act, q):
        self.t = t          # timestamp
        self.hr = hr
        self.sk = sk
        self.tp = tp
        self.act = act      # activity level
        self.q = q          # signal quality


class Session:
    def __init__(self, sid, p, obs, total):
        self.sid = sid      # session ID
        self.p = p          # Person
        self.obs = obs      # Valid observations
        self.total = total  # Total Number of observations in session