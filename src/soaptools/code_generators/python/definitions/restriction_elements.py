from dataclasses import dataclass
from typing import List
import re
from soaptools.code_generators.python.definitions.exceptions import RestrictionException


class RestrictionRule:
    def validate(self, value):
        raise NotImplementedError()


@dataclass
class Restriction:
    rules: List[RestrictionRule] = None

    def validate(self, value):
        for rule in self.rules:
            rule.validate(value)


class MinMaxAbstractClass(RestrictionRule):
    required_methods = ["__lt__", "__gt__", "__eq__"]

    def __init__(self, threshold_val):
        if any([not hasattr(threshold_val, method_name) for method_name in self.required_methods]):
            raise TypeError(f"threshold_val={threshold_val} doesn't implement one of [<>=] operators")
        self.threshold_val = threshold_val


class MinInclusive(MinMaxAbstractClass):

    def __init__(self, min):
        super(MinInclusive, self).__init__(min)

    def validate(self, value):
        if value < self.threshold_val:
            raise RestrictionException(f"Value {value} is lower than {self.threshold_val}")


class MaxInclusive(MinMaxAbstractClass):

    def __init__(self, max):
        super(MaxInclusive, self).__init__(max)

    def validate(self, value):
        if value > self.threshold_val:
            raise RestrictionException(f"Value {value} is larger than {self.threshold_val}")


class Enumeration(RestrictionRule):
    def __init__(self, accepted_values):
        self.accepted_values = accepted_values

    def validate(self, value):
        if value not in self.accepted_values:
            raise RestrictionException(f"Value {value} not in {str(self.accepted_values)}")


class Pattern(RestrictionRule):
    def __init__(self, pattern):
        self.pattern = pattern

    def validate(self, value):
        if re.fullmatch(self.pattern, value):
            raise RestrictionException(f"Value {value} doesn't match pattern {self.pattern}")
