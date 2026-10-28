"""
Reference-number generator for MyBank transaction records.

Format: MB-{PREFIX}-{YYYYMMDD}-{XXXXXXXX}
  PREFIX   — 3-letter type code (DEP, WDL, TRF, IBT, FEE, ACC)
  YYYYMMDD — UTC date of generation
  XXXXXXXX — 8 uppercase hex characters from a cryptographically-secure
              random source (secrets module), giving ~4 billion combinations
              per prefix per day, effectively collision-free in normal use.

All generation is server-side only.  Frontend forms must never supply these
values; the backend ignores any client-provided reference and always uses
the value generated here.
Customer transfer retries use a secret-derived stable reference so duplicate
submissions can be recognized without adding a database column.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timezone


def generate_reference(prefix: str) -> str:
    """Return a unique MB-{PREFIX}-YYYYMMDD-XXXXXXXX reference string.

    Args:
        prefix: Short uppercase transaction type label, e.g. "DEP", "WDL".

    Returns:
        A string such as ``MB-DEP-20261028-3A7F9C2E``.
    """
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    rand_part = secrets.token_hex(4).upper()          # 8 hex chars
    return f"MB-{prefix}-{date_str}-{rand_part}"


def generate_idempotent_reference(
    prefix: str,
    identity: str,
    key: str,
    secret: str,
) -> str:
    """Return a stable, server-generated reference for a retried request."""
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{identity}:{key}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()
    return f"MB-{prefix}-IDEM-{digest}"


def generate_account_number() -> str:
    """Return a short customer-facing account number for a new account.

    Format: ``MB`` followed by ten random digits. Existing account numbers
    are not changed when this generator is updated.
    """
    return f"MB{secrets.randbelow(10_000_000_000):010d}"
