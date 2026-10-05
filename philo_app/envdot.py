"""Small env helper so the app can find config in a non-source-controlled .env."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | None = None) -> None:
    """Minimal .env loader — sets os.environ, never overrides existing."""
    p = Path(path) if path else Path(__file__).resolve().parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        os.environ.setdefault(key, val)
