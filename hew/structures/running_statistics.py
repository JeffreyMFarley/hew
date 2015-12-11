# -----------------------------------------------------------------------------

class RunningStatistics:
    """ This encapsulates statistical measures that can be queried at any time """
    def __init__(self):
        self.reset()

    def reset(self):
        self.count = 0
        self.sum = 0
        self.square_sum = 0
        self.min = float("inf")
        self.max = -float("inf")

    @property
    def mean(self):
        return self.sum / self.count if self.count > 0 else 0

    @property
    def variance(self):
         if self.count < 1:
             return 0
         
         return (self.square_sum - 
                ((self.sum * self.sum) / self.count)
                ) / (self.count - 1)

    @property
    def standard_deviation(self):
        import math
        return math.sqrt(self.variance)

    def __iadd__(self, value):
        self.count += 1;
        self.sum += value;
        self.square_sum += (value * value);

        if value < self.min:
            self.min = value;

        if value > self.max:
            self.max = value;

        return self

    def __isub__(self, value):
        if self.count < 1:
            return

        self.count -= 1;
        self.sum -= value;
        self.square_sum -= (value * value);

        return self
