"""Type definitions for train ticket pricing system."""

from enum import Enum


class CoachType(Enum):
    AC_3 = "3AC"
    SLEEPER = "Sleeper"
    AC_2 = "2AC"
    AC_1 = "1AC"
    GENERAL = "General"


class TicketType(Enum):
    GENERAL = "General"
    TATKAL = "Tatkal"
