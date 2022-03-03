class ValidationException(Exception):
    def __init__(self, reason):
        self.reason = reason


class RestrictionException(ValidationException):
    pass

