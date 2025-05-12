import hashlib

def create_commitment(ttl, length, protocol):
    """Create a SHA256 hash commitment of the input values."""
    message = f"{ttl}|{length}|{protocol}"
    hash_value = hashlib.sha256(message.encode()).hexdigest()
    return hash_value

def verify_commitment(ttl, length, protocol, given_hash):
    """Verify if the provided inputs match the given hash."""
    return create_commitment(ttl, length, protocol) == given_hash
