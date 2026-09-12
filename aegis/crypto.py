"""Authenticated local message encryption using Fernet (AES-based AEAD construction)."""

from cryptography.fernet import Fernet, InvalidToken


def generate_key():
    return Fernet.generate_key().decode('ascii')


def encrypt_message(message, key):
    return Fernet(key.encode('ascii')).encrypt(message.encode('utf-8')).decode('ascii')


def decrypt_message(token, key):
    try:
        return Fernet(key.encode('ascii')).decrypt(token.encode('ascii')).decode('utf-8')
    except InvalidToken as exc:
        raise ValueError('Invalid key or message token') from exc


def message_demo():
    key = generate_key()
    token = encrypt_message('AEGIS secure channel online.', key)
    return {
        'algorithm': 'Fernet / AES-based authenticated encryption',
        'ciphertext': token,
        'key_generated': True,
        'scope': 'local demonstration',
    }
