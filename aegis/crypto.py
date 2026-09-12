import base64
import hashlib
import secrets


def generate_key():
    return secrets.token_urlsafe(32)


def _key_bytes(key):
    return hashlib.sha256(key.encode('utf-8')).digest()


def encrypt_message(message, key):
    raw = message.encode('utf-8')
    stream = _key_bytes(key)
    encrypted = bytes(value ^ stream[index % len(stream)] for index, value in enumerate(raw))
    return base64.urlsafe_b64encode(encrypted).decode('ascii')


def decrypt_message(token, key):
    encrypted = base64.urlsafe_b64decode(token.encode('ascii'))
    stream = _key_bytes(key)
    raw = bytes(value ^ stream[index % len(stream)] for index, value in enumerate(encrypted))
    return raw.decode('utf-8')


def message_demo():
    key = generate_key()
    token = encrypt_message('AEGIS secure channel online.', key)
    return {'algorithm': 'DEMO-XOR / REPLACE WITH REVIEWED AEAD', 'ciphertext': token, 'key_generated': True}
