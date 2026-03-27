from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"


class BrightDataError(RuntimeError):
    pass


def fetch_page(url: str) -> str:
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    zone = os.getenv("BRIGHTDATA_UNLOCKER_ZONE")

    if not api_key:
        raise BrightDataError("Missing BRIGHTDATA_API_KEY")
    if not zone:
        raise BrightDataError("Missing BRIGHTDATA_UNLOCKER_ZONE")

    payload = {
        "zone": zone,
        "url": url,
        "format": "raw",
    }
    body = json.dumps(payload).encode("utf-8")

    req = Request(
        BRIGHTDATA_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            return content
    except HTTPError as exc:
        raise BrightDataError(f"Bright Data HTTP error: {exc.code}") from exc
    except URLError as exc:
        raise BrightDataError(f"Bright Data URL error: {exc.reason}") from exc
