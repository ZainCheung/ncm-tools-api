import binascii
import os
import base64
from Crypto.Cipher import AES

modulus = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629"
    "ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d"
    "813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 ")
nonce = "0CoJUm6Qyw8W8jud"
pubKey = "010001"


def encrypt(text):
    # Random String Generator
    sec_key = str(binascii.hexlify(os.urandom(16))[:16], encoding="utf-8")
    enc_text = aes_encrypt(aes_encrypt(text, nonce), sec_key)
    enc_sec_key = rsa_encrypt(sec_key, pubKey, modulus)
    return {"params": enc_text, "encSecKey": enc_sec_key}


# AES Encrypt
def aes_encrypt(text, sec_key):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(sec_key.encode("utf8"), 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text.encode("utf8"))
    ciphertext = str(base64.b64encode(ciphertext), encoding="utf-8")
    return ciphertext


# RSA Encrypt
def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(text.encode("utf-8").hex(), 16)**int(pub_key, 16) % int(
        modulus, 16)
    return format(rs, "x").zfill(256)
