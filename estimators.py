"""
Module to deal with stat estimation
"""
from abc import ABC, abstractmethod
from typing import *
import numpy as np


class Estimator(ABC):
    """
    Class to estimate a certain statistic

    Attributes:
        current_estimate: a numpy vector giving the probability of each option
        noptions: int, the number of options
        xvals: the range of possible values of the statistic to estimate
    """
    def __init__(self, noptions: int):
        self.current_estimate = np.ones((noptions,)) / noptions

    @property
    def noptions(self) -> int:
        return self.current_estimate.shape[0]

    @property
    def xvals(self) -> np.ndarray:
        return np.arange(self.noptions)

    def set_prior(self, prior: np.ndarray):
        """
        Sets the prior distribution

        :param prior: an ndarray, the prior distribution
        """
        assert sum(prior) == 1
        self.current_estimate = prior

    @abstractmethod
    def model(self, measurement) -> np.ndarray:
        """
        Calculates the probability of the measurement for each option

        :param measurement: the most recent measurement
        :return: a numpy vector with (noptions) elements, giving the probability of this measurement given the
            estimated value
        """
        pass

    def update(self, measurement):
        """
        Update the current belief given a measurement, as per Bayes' Rule

        :param measurement: the measured value
        """
        self.current_estimate *= self.model(measurement)
        self.current_estimate /= np.sum(self.current_estimate)

    def map(self) -> float:
        """
        :return: a float, the Maximum A Posteriori (or the average of them in the case of multiple) of the current estimate
        """
        highest = np.max(self.current_estimate)
        modes = self.current_estimate == highest
        return np.sum(self.current_estimate[modes]) / len(modes)

    def mean(self) -> float:
        """
        :return: a float, the weighted mean of the current estimate
        """
        return sum(self.current_estimate * np.arange(self.current_estimate.shape[0]))


class ModifierEstimator(Estimator):
    def __init__(self):
        super().__init__(21)  # -5 to 15

    @property
    def xvals(self) -> np.ndarray:
        return np.arange(self.noptions) - 5

    def model(self, measurement: int) -> np.ndarray:
        """
        Calculates the probability of the measurement for each option

        :param measurement: an int, the most recent roll
        :return: a numpy vector with (noptions) elements, giving the probability of this measurement given the
            estimated value
        """
        poss_rolls = measurement - self.xvals
        in_range = (1 <= poss_rolls) & (poss_rolls <= 20)
        return in_range / 20


class ACEstimator(Estimator):
    def __init__(self):
        super().__init__(31)  # 0 to 30

    def model(self, measurement: Tuple[int, bool]):
        """
        Calculates the probability of the measurement for each option

        :param measurement: a tuple - the most recent roll followed by whether it hit
        :return: a numpy vector with (noptions) elements, giving the probability of this measurement given the
            estimated value
        """
        roll, hit = measurement
        if hit:
            return self.xvals <= roll
        return self.xvals > roll
