import hashlib
import hmac
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


def verify_github_signature(
    raw_payload_bytes: bytes,
    signature_header: Optional[str],
    secret_override: Optional[str] = None
) -> bool:
    """
    Verify incoming GitHub webhook HMAC-SHA256 signature (X-Hub-Signature-256).
    """
    secret = secret_override or settings.GITHUB_WEBHOOK_SECRET
    
    # In development mode, allow empty secret for local testing
    if not secret and settings.ENVIRONMENT == "development":
        logger.warning("GITHUB_WEBHOOK_SECRET is not set; skipping signature verification in development.")
        return True

    if not secret or not signature_header:
        logger.error("Missing webhook secret or X-Hub-Signature-256 header.")
        return False

    if not signature_header.startswith("sha256="):
        logger.error("Invalid signature header format; must start with 'sha256='.")
        return False

    expected_signature = signature_header.split("sha256=")[1]
    
    mac = hmac.new(secret.encode("utf-8"), msg=raw_payload_bytes, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)
