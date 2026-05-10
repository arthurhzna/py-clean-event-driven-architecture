from dataclasses import dataclass


@dataclass
class ScreenshotState:
    url: str | None = None
    should_send: bool = False