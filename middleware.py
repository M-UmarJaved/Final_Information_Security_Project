# middleware.py
# Payload signing and verification using HMAC-SHA256

import hmac
import hashlib
import json
import time
import re
from config import SECRET_KEY

def sign_payload(payload: dict) -> dict:
    """
    Add a cryptographic signature and timestamp to the payload.
    Any modification to the payload will invalidate the signature.
    """
    payload_copy = dict(payload)
    payload_copy['timestamp'] = int(time.time())

    # Sort keys to ensure consistency between sign and verify
    payload_str = json.dumps(payload_copy, sort_keys=True, separators=(',', ':'))

    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

    payload_copy['signature'] = signature
    return payload_copy

def verify_payload(payload: dict) -> tuple:
    """
    Verify the payload signature and check timestamp freshness.
    Returns: (is_valid: bool, reason: str)
    """
    if not isinstance(payload, dict):
        return False, 'Invalid JSON payload'

    # Check existence of required fields
    if 'signature' not in payload or 'timestamp' not in payload:
        return False, 'Missing signature or timestamp'

    received_sig = payload.get('signature')
    timestamp = payload.get('timestamp', 0)

    if not isinstance(received_sig, str) or not re.fullmatch(r'[a-f0-9]{64}', received_sig):
        return False, 'Invalid signature format'

    if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
        return False, 'Invalid timestamp type'

    # Replay attack prevention – 30 second window
    if abs(time.time() - timestamp) > 30:
        return False, 'Request expired – possible replay attack'

    # Recompute signature from the rest of the payload
    payload_to_verify = dict(payload)
    payload_to_verify.pop('signature', None)
    payload_str = json.dumps(payload_to_verify, sort_keys=True, separators=(',', ':'))
    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(received_sig, expected_sig):
        return False, 'Signature mismatch – payload was tampered!'

    return True, 'Valid'
