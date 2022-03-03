import hashlib
import os
import re
import random

import requests

from soaptools.helpers.validators import is_url


def find_by_predicate(iterable, predicate):
    return next((element for element in iterable if predicate(element) is True), None)


def chain_hasattr(obj, path):
    current = obj
    for subelement in path.split("."):
        try:
            current = getattr(current, subelement)
        except AttributeError:
            return False
    return True


def chain_getattr(obj, path, default="totally_default"):
    current = obj
    for subelement in path.split("."):
        if default != "totally_default":
            current = getattr(current, subelement, default)
        else:
            current = getattr(current, subelement)
    return current


def get_content_from_uri(uri: str) -> str:
    if is_url(uri):
        return requests.get(uri).text
    elif os.path.isfile(uri):
        return open(uri, encoding="utf-8").read()
    raise Exception(f"{uri} is not valid URL nor filesystem path")


def format_code(code: str) -> str:
    rand_file_name = hashlib.sha1(random.randbytes(10)).hexdigest() + ".py"
    open(rand_file_name, mode="w").write(code)

    os.system(f"black {rand_file_name}")
    formatted_code = open(rand_file_name).read()
    os.remove(rand_file_name)

    return formatted_code


def do_math_operation(obj1, obj2, operation):
    if operation == "+":
        return obj1 + obj2
    if operation == "-":
        return obj1 - obj2
    else:
        raise ValueError(f"unknown operation {operation}")


def are_numbers_signs_equal(val1, val2):
    return val1 >= 0 and val2 >= 0 or val1 < 0 and val2 < 0


class Logger:
    @staticmethod
    def failure(message, exit_code=1):
        print("[FAILURE] " + message)
        exit(exit_code)

    @staticmethod
    def warning(message):
        print("[WARNING] " + message)

    @staticmethod
    def info(message):
        print("[INFO] " + message)


class Duration:
    """
    ASSUMPTIONS:
        year == 12 months or 365 days
        month == 30 days
    TODO:
        - add support for weeks
        - add __add__, __sub__, __mul__, __div__ math operations
    """

    is_negative = False
    _years = 0
    _months = 0
    _days = 0
    _hours = 0
    _minutes = 0
    _seconds = 0
    __time_attributes = [
        "years",
        "months",
        "days",
        "hours",
        "minutes",
        "seconds",
    ]

    def __init__(self, years=0, months=0, days=0, hours=0, minutes=0, seconds=0, is_negative=False):
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.is_negative = is_negative
        self.__simplify()

    @classmethod
    def from_iso8601(cls, text):
        # add simplifying
        duration_regex = re.compile(r"^-?P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$")
        if not duration_regex.fullmatch(text):
            raise ValueError("Not valid ISO 8601 duration string")
        date, time = text.split("T")
        if re.search("\d+W", date):
            raise ValueError("Weeks are not supported")

        kwargs = {
            "years": re.search("\d+Y", date),
            "months": re.search("\d+M", date),
            "days": re.search("\d+D", date),
            "hours": re.search("\d+H", time),
            "minutes": re.search("\d+M", time),
            "seconds": re.search("\d+(\.\d+)?S", time),
        }
        for key, val in kwargs.items():
            if val is None:
                val = 0
            else:
                val = val.group(0)[:-1]
                if key == "seconds":
                    val = float(val)
                else:
                    val = int(val)
            kwargs[key] = val
        kwargs["is_negative"] = text[0] == "-"
        return cls(**kwargs)

    def __compare(self, other):
        if not isinstance(other, Duration):
            raise TypeError("Only Duration classes can be compared")
        if self.is_negative and not other.is_negative:
            return "lesser"
        if not self.is_negative and other.is_negative:
            return "greater"

        for attribute in self.__time_attributes:
            if getattr(self, attribute) > getattr(other, attribute):
                return "greater"
            elif getattr(self, attribute) < getattr(other, attribute):
                return "lesser"
        return "equal"

    def __lt__(self, other):
        return self.__compare(other) == "lesser"

    def __gt__(self, other):
        return self.__compare(other) == "greater"

    def __eq__(self, other):
        return self.__compare(other) == "equal"

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    @property
    def years(self):
        return self._years

    @years.setter
    def years(self, value):
        if not isinstance(value, int):
            raise TypeError("Only integers are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._years = value

    @property
    def months(self):
        return self._months

    @months.setter
    def months(self, value):
        if not isinstance(value, int):
            raise TypeError("Only integers are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._months = value

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, value):
        if not isinstance(value, int):
            raise TypeError("Only integers are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._days = value

    @property
    def hours(self):
        return self._hours

    @hours.setter
    def hours(self, value):
        if not isinstance(value, int):
            raise TypeError("Only integers are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._hours = value

    @property
    def minutes(self):
        return self._minutes

    @minutes.setter
    def minutes(self, value):
        if not isinstance(value, int):
            raise TypeError("Only integers are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._minutes = value

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise TypeError("Only integers or floats are accepted")
        if not value >= 0:
            raise ValueError("Only positive values are accepted")
        self._seconds = float(value)

    def __simplify(self):
        self._seconds, remainder = divmod(self._seconds, 60)
        self._minutes += int(remainder)
        self._minutes, remainder = divmod(self._minutes, 60)
        self._hours += remainder
        self._hours, remainder = divmod(self._hours, 24)
        self._days += remainder

        # converting to all days first and start collecting from years because
        # 1 year == 365 days but 1 month == 30 days so 12 months == 360 days
        all_days = self._days + 30 * self._months + 365 * self._years
        self._years, all_days = divmod(all_days, 365)
        self._months, self._days = divmod(all_days, 30)

    def __repr__(self):
        attributes_parsed = " ".join(
            [
                f"{attribute}=" + str(getattr(self, attribute))
                for attribute in ["is_negative"] + self.__time_attributes
            ]
        )
        return f"<Duration {attributes_parsed}>"

    def to_iso8601_string(self):
        date_elements = [
            ("years", "Y"),
            ("months", "M"),
            ("days", "D"),
        ]
        time_elements = [
            ("hours", "H"),
            ("minutes", "S"),
            ("seconds", "S"),
        ]
        out = "P"

        for attr_name, symbol in date_elements:
            value = getattr(self, attr_name)
            if not value:
                continue
            out += f"{value}{symbol}"
        for attr_name, symbol in time_elements:
            value = getattr(self, attr_name)
            if not value:
                continue
            if "T" not in out:
                out += "T"
            out += f"{value}{symbol}"
        return out
