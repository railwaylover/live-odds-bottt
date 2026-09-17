"""HTTP helper: JSON GET with browser UA, timeout, and polite errors."""
from __future__ import annotations

import json
import urllib.request

from .. import config


def get_json(url: str, timeout: int = 15, params: dict | None = None,
             user_agent: str | None = None) -> object:
    if params:
        from urllib.parse import urlencode
        url += ("&" if "?" in url else "?") + urlencode(params)
    headers = {"User-Agent": user_agent or config.USER_AGENT,
               "Accept": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)
