"""Parse YouTube watch, share, embed, and short links into a video id."""

import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_ID_RE = re.compile(r"^[\w-]{11}$")
_HOSTS = {"youtube.com", "m.youtube.com", "youtube-nocookie.com", "youtu.be"}


def parse_youtube_video_id(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    if YOUTUBE_ID_RE.match(raw):
        return raw

    candidate = raw if re.match(r"^https?://", raw, re.IGNORECASE) else f"https://{raw}"
    try:
        parsed = urlparse(candidate)
    except ValueError:
        return ""

    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host not in _HOSTS:
        return ""

    if host == "youtu.be":
        video_id = next((part for part in parsed.path.split("/") if part), "")
        return video_id if YOUTUBE_ID_RE.match(video_id) else ""

    query_id = parse_qs(parsed.query).get("v", [""])[0]
    if YOUTUBE_ID_RE.match(query_id):
        return query_id

    parts = [part for part in parsed.path.split("/") if part]
    for marker in ("embed", "shorts", "live", "v"):
        if marker in parts:
            index = parts.index(marker)
            video_id = parts[index + 1] if index + 1 < len(parts) else ""
            if YOUTUBE_ID_RE.match(video_id):
                return video_id
    return ""


def canonical_youtube_url(value: str) -> str:
    """Return a watch URL, or an empty string when the input is blank.

    Raises ValueError when the input is not a YouTube link.
    """
    raw = (value or "").strip()
    if not raw:
        return ""
    video_id = parse_youtube_video_id(raw)
    if not video_id:
        raise ValueError("Enter a valid YouTube link or video ID")
    return f"https://www.youtube.com/watch?v={video_id}"
