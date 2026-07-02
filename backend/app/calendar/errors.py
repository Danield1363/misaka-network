class CalendarError(Exception):
    pass


class EventNotFoundError(CalendarError):
    pass


class ReminderNotFoundError(CalendarError):
    pass


class CalendarValidationError(CalendarError):
    pass