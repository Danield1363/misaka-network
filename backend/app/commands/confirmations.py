from dataclasses import dataclass, field
import time
import uuid


@dataclass
class PendingConfirmation:
    id: str
    intent: str
    tool_name: str
    parameters: dict
    message: str
    created_at: float = field(default_factory=time.time)
    status: str = "pending"


class ConfirmationManager:
    def __init__(self) -> None:
        self._pending: dict[str, PendingConfirmation] = {}

    def create_confirmation(
        self,
        intent: str,
        tool_name: str,
        parameters: dict,
        message: str
    ) -> PendingConfirmation:
        conf_id = str(uuid.uuid4())[:8]
        confirmation = PendingConfirmation(
            id=conf_id,
            intent=intent,
            tool_name=tool_name,
            parameters=parameters,
            message=message
        )
        self._pending[conf_id] = confirmation
        return confirmation

    def approve(self, confirmation_id: str) -> PendingConfirmation | None:
        conf = self._pending.get(confirmation_id)
        if conf:
            conf.status = "approved"
        return conf

    def deny(self, confirmation_id: str) -> PendingConfirmation | None:
        conf = self._pending.get(confirmation_id)
        if conf:
            conf.status = "denied"
        return conf

    def get_pending(self) -> list[PendingConfirmation]:
        return [c for c in self._pending.values() if c.status == "pending"]

    def approve_latest(self) -> PendingConfirmation | None:
        pending = self.get_pending()
        if not pending:
            return None
        latest = max(pending, key=lambda c: c.created_at)
        return self.approve(latest.id)

    def cleanup(self, max_age_seconds: float = 300) -> int:
        now = time.time()
        expired = [
            cid for cid, c in self._pending.items()
            if now - c.created_at > max_age_seconds
        ]
        for cid in expired:
            del self._pending[cid]
        return len(expired)


confirmation_manager = ConfirmationManager()
