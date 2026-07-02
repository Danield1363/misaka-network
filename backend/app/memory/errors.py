class MemoryError(Exception):
    pass


class MemoryNotFoundError(MemoryError):
    pass


class MemoryValidationError(MemoryError):
    pass