class LLMError(Exception):
    pass


class ProviderNotFoundError(LLMError):
    pass


class ProviderUnavailableError(LLMError):
    pass


class GenerationError(LLMError):
    pass