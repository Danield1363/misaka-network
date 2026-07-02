import re


class ResponseFormatter:
    def __init__(
        self,
        suffix_enabled: bool = True,
        suffix_text: str = "diz Misaka Misaka.",
    ) -> None:
        self.suffix_enabled = suffix_enabled
        self.suffix_text = suffix_text

    def format(self, text: str) -> str:
        text = self._strip_markdown(text)
        text = self._clean_spaces(text)
        text = self._ensure_punctuation(text)
        if self.suffix_enabled:
            text = self._append_suffix(text)
        return text

    def _strip_markdown(self, text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"__(.+?)__", r"\1", text)
        text = re.sub(r"_(.+?)_", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)
        text = re.sub(r"~~(.+?)~~", r"\1", text)
        return text

    def _clean_spaces(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _ensure_punctuation(self, text: str) -> str:
        if text and text[-1] not in ".!?;:":
            text += "."
        return text

    def _append_suffix(self, text: str) -> str:
        if self.suffix_text.lower() in text.lower():
            return text
        return f"{text.rstrip('.!?;:')} {self.suffix_text}"
