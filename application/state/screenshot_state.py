from dataclasses import dataclass
from typing import Optional

@dataclass
class ScreenshotState:
    url: Optional[str] = None
    flag: bool = False