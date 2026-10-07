"""Official YMCA Ghana membership types."""

from typing import Optional

MEMBERSHIP_TYPES = (
    "Junior",
    "Associate",
    "Full",
    "Life Membership",
    "Honorary",
)

_BY_KEY = {name.casefold(): name for name in MEMBERSHIP_TYPES}


def coerce_membership_type(value: Optional[str], *, strict: bool) -> Optional[str]:
    """Return the canonical membership label.

    Signup must use an official type. Updates may keep a label already stored
    on an older account when it is sent back unchanged.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    official = _BY_KEY.get(text.casefold())
    if official:
        return official
    if strict:
        allowed = ", ".join(MEMBERSHIP_TYPES)
        raise ValueError(f"Membership type must be one of: {allowed}")
    return text
