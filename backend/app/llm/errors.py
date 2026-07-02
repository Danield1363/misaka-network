class LLMError(Exception):
    pass


class ProviderNotFoundError(LLMError):
    pass


class ProviderUnavailableError(LLMError):
    pass


class GenerationError(LLMError):
    pass


class QuotaExceededError(LLMError):
    def __init__(self, model: str = "", error_type: str = "quota_exceeded"):
        self.model = model
        self.error_type = error_type
        super().__init__(f"Quota exceeded for model {model}: {error_type}")


class RateLimitError(LLMError):
    def __init__(self, model: str = ""):
        self.model = model
        super().__init__(f"Rate limited for model {model}")


class ModelNotFoundError(LLMError):
    def __init__(self, model: str = ""):
        self.model = model
        super().__init__(f"Model not found: {model}")
