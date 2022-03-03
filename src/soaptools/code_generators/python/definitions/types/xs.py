import datetime
import math

from soaptools.code_generators.python.definitions.types import SimpleType
from soaptools.helpers.py import Duration
from soaptools.code_generators.python.definitions.exceptions import ValidationException
from soaptools.soap.namespaces import XS_NAMESPACE


class AnyUriSimpleType(SimpleType):
    # todo: add validation
    class Meta:
        name = "anyURI"
        targetNamespace = XS_NAMESPACE


class Base64BinarySimpleType(SimpleType):
    # todo: add validation
    class Meta:
        name = "base64Binary"
        targetNamespace = XS_NAMESPACE


class BooleanSimpleType(SimpleType):
    def __init__(self, value):
        if isinstance(value, str) and value in ["true", "false"]:
            value = (value == "true")
        elif not isinstance(value, bool):
            raise ValidationException("Value must be in [True, False, 'true', 'false']")
        super().__init__(value)

    @property
    def xml_value(self):
        return "true" if self._value is True else "false"

    class Meta:
        name = "boolean"
        targetNamespace = XS_NAMESPACE


class DateSimpleType(SimpleType):
    def __init__(self, value):
        if isinstance(value, str):
            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        elif isinstance(value, datetime.datetime):
            value = value.date()
        else:
            raise ValidationException("String in format: '%Y-%m-%d' required or datetime or date")
        super().__init__(value)

    @property
    def xml_value(self):
        return self._value.strptime("%Y-%m-%d")

    class Meta:
        name = "date"
        targetNamespace = XS_NAMESPACE


class DateTimeSimpleType(SimpleType):
    def __init__(self, value):
        if isinstance(value, str):
            value = datetime.datetime.fromisoformat(value.replace("Z", ""))
        elif isinstance(value, datetime.datetime):
            value = value.date()
        elif not isinstance(value, datetime.date):
            raise ValidationException("String in format: '%Y-%m-%d' required or datetime or date")
        super().__init__(value)

    @property
    def xml_value(self):
        return self._value.isoformat() + "Z"

    class Meta:
        name = "dateTime"
        targetNamespace = XS_NAMESPACE


class DateTimeStampSimpleType(DateTimeSimpleType):
    """
    Like DateTime but explicit timezone info is required
    """
    class Meta:
        name = "dateTimeStamp"
        targetNamespace = XS_NAMESPACE


class DecimalSimpleType(SimpleType):
    values_range = [-math.inf, math.inf]

    def __init__(self, value):
        if isinstance(value, str):
            value = value.replace(",", ".")
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        if value.__class__ not in [int, float]:
            raise ValidationException("Only integer, float, str values are accepted")
        super().__init__(value)
        if self._value < self.values_range[0] or self._value > self.values_range[1]:
            raise ValidationException(f"Value {value} not in range [{self.values_range[0]}, {self.values_range[1]}]")

    class Meta:
        name = "decimal"
        targetNamespace = XS_NAMESPACE


class IntegerSimpleType(DecimalSimpleType):

    class Meta:
        name = "integer"
        targetNamespace = XS_NAMESPACE


class LongSimpleType(IntegerSimpleType):

    class Meta:
        name = "long"
        targetNamespace = XS_NAMESPACE


class IntSimpleType(LongSimpleType):
    values_range = [-2147483648, 2147483647]

    class Meta:
        name = "int"
        targetNamespace = XS_NAMESPACE


class ShortSimpleType(IntSimpleType):
    values_range = [-32768, 32767]

    class Meta:
        name = "short"
        targetNamespace = XS_NAMESPACE


class ByteSimpleType(ShortSimpleType):
    values_range = [-128, 127]

    class Meta:
        name = "byte"
        targetNamespace = XS_NAMESPACE


class NonNegativeIntegerSimpleType(IntegerSimpleType):
    values_range = [0, math.inf]

    class Meta:
        name = "nonNegativeInteger"
        targetNamespace = XS_NAMESPACE


class PositiveIntegerSimpleType(NonNegativeIntegerSimpleType):

    def __init__(self, value):
        super().__init__(value)
        if self._value <= 0:
            raise ValidationException("Only positive integers are accepted")

    class Meta:
        name = "positiveInteger"
        targetNamespace = XS_NAMESPACE


class UnsignedLongSimpleType(NonNegativeIntegerSimpleType):
    class Meta:
        name = "unsignedLong"
        targetNamespace = XS_NAMESPACE


class UnsignedIntSimpleType(UnsignedLongSimpleType):
    class Meta:
        name = "unsignedInt"
        targetNamespace = XS_NAMESPACE


class UnsignedShortSimpleType(UnsignedIntSimpleType):
    class Meta:
        name = "unsignedShort"
        targetNamespace = XS_NAMESPACE


class UnsignedByteSimpleType(UnsignedShortSimpleType):
    class Meta:
        name = "unsignedByte"
        targetNamespace = XS_NAMESPACE


class NonPositiveIntegerSimpleType(IntegerSimpleType):
    values_range = [-math.inf, 0]

    class Meta:
        name = "nonPositiveInteger"
        targetNamespace = XS_NAMESPACE


class NegativeIntegerSimpleType(NonPositiveIntegerSimpleType):

    def __init__(self, value):
        super().__init__(value)
        if self._value >= 0:
            raise ValidationException("Only negative integers are accepted")

    class Meta:
        name = "negativeInteger"
        targetNamespace = XS_NAMESPACE


class DoubleSimpleType(SimpleType):
    class Meta:
        name = "double"
        targetNamespace = XS_NAMESPACE


class DurationSimpleType(SimpleType):

    def __init__(self, value):
        # options: datetime.timedelta, string, own implementation
        if isinstance(value, str):
            try:
                value = Duration.from_iso8601(value)
            except Exception:
                raise ValidationException(f"{value} is not valid ISO 8601 duration string")
        elif not isinstance(value, Duration):
            raise TypeError(f"Duration fields accepts only ISO 8601 duration string or Duration")

        super().__init__(value)

    def xml_value(self):
        return str(self._value)

    class Meta:
        name = "duration"
        targetNamespace = XS_NAMESPACE


class DayTimeDurationSimpleType(SimpleType):
    class Meta:
        name = "dayTimeDuration"
        targetNamespace = XS_NAMESPACE


class YearMonthDurationSimpleType(SimpleType):
    class Meta:
        name = "yearMonthDuration"
        targetNamespace = XS_NAMESPACE


class FloatSimpleType(SimpleType):
    def __init__(self, value):
        if isinstance(value, str):
            value = float(value)
        if value.__class__ not in [int, float]:
            raise ValidationException("Only integer, float, str values are accepted")
        super().__init__(value)

    class Meta:
        name = "float"
        targetNamespace = XS_NAMESPACE


class GDaySimpleType(SimpleType):
    class Meta:
        name = "gDay"
        targetNamespace = XS_NAMESPACE


class GMonthSimpleType(SimpleType):
    class Meta:
        name = "gMonth"
        targetNamespace = XS_NAMESPACE


class GMonthDaySimpleType(SimpleType):
    class Meta:
        name = "gMonthDay"
        targetNamespace = XS_NAMESPACE


class GYearSimpleType(SimpleType):
    class Meta:
        name = "gYear"
        targetNamespace = XS_NAMESPACE


class GYearMonthSimpleType(SimpleType):
    class Meta:
        name = "gYearMonth"
        targetNamespace = XS_NAMESPACE


class HexBinarySimpleType(SimpleType):
    class Meta:
        name = "hexBinary"
        targetNamespace = XS_NAMESPACE


class NotationSimpleType(SimpleType):
    class Meta:
        name = "NOTATION"
        targetNamespace = XS_NAMESPACE


class QNameSimpleType(SimpleType):
    class Meta:
        name = "QName"
        targetNamespace = XS_NAMESPACE


class StringSimpleType(SimpleType):
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValidationException("value must be string instance")
        super().__init__(value)

    class Meta:
        name = "string"
        targetNamespace = XS_NAMESPACE


class NormalizedStringSimpleType(SimpleType):
    class Meta:
        name = "normalizedString"
        targetNamespace = XS_NAMESPACE


class TokenSimpleType(NormalizedStringSimpleType):
    class Meta:
        name = "token"
        targetNamespace = XS_NAMESPACE


class LanguageSimpleType(TokenSimpleType):
    class Meta:
        name = "language"
        targetNamespace = XS_NAMESPACE


class NameSimpleType(TokenSimpleType):
    class Meta:
        name = "Name"
        targetNamespace = XS_NAMESPACE


class NCNameSimpleType(TokenSimpleType):
    class Meta:
        name = "NCName"
        targetNamespace = XS_NAMESPACE


class EntitySimpleType(NCNameSimpleType):
    class Meta:
        name = "ENTITY"
        targetNamespace = XS_NAMESPACE


class IdSimpleType(NCNameSimpleType):
    class Meta:
        name = "ID"
        targetNamespace = XS_NAMESPACE


class IdRefSimpleType(NCNameSimpleType):
    class Meta:
        name = "IDREF"
        targetNamespace = XS_NAMESPACE


class NmTokenSimpleType(TokenSimpleType):
    class Meta:
        name = "NMTOKEN"
        targetNamespace = XS_NAMESPACE


class TimeSimpleType(SimpleType):
    class Meta:
        name = "time"
        targetNamespace = XS_NAMESPACE
