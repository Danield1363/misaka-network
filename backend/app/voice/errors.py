class VoiceError(Exception):
    def __init__(self, safe_message: str, code: str = "voice_error") -> None:
        self.safe_message = safe_message
        self.code = code
        super().__init__(safe_message)


class VoiceProviderNotConfigured(VoiceError):
    def __init__(self) -> None:
        super().__init__(
            "Transcricao de voz nao configurada no backend.",
            "voice_provider_not_configured",
        )


class VoiceValidationError(VoiceError):
    pass

