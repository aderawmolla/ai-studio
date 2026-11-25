"""Exceptions that carry a headline reason plus technical detail."""


class StageAbort(RuntimeError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail or reason