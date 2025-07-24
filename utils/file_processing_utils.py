import textwrap
import os
import sys
from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# convert byte array to bit string
def bytes_to_bits(bytes):
            
    bits = ''.join(f"{byte:08b}" for byte in bytes)

    return bits


# convert bit string to byte array
def bits_to_bytes(bits):

    val = int(bits, 2)
    n_B = len(bits) // 8

    return val.to_bytes(n_B, byteorder="big")


# zero pad and wrap to equal k length blocks
def pad_wrap(bits, k):

    mod = len(bits) % k
    if mod != 0:
        bits += "0" * (k-mod)
    
    return textwrap.wrap(bits, k)


# merge binary blocks to string and unpad 0s
def merge_unpad(bits):

    bits = "".join(bits)
    mod = len(bits) % 8

    return bits[:len(bits) - mod]


def encrypt(plaintext, key):

    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = cipher.encrypt(plaintext)

    return iv, ciphertext


def decrypt(iv, ciphertext, key):

    cipher = AES.new(key, AES.MODE_CFB, iv)
    plaintext = cipher.decrypt(ciphertext)
    
    return plaintext


def hash_digest(password):

    h = SHA256.new(data=password.encode())
    
    return h.digest()


# process secret file to embedding bits (encrypted)
# function returns two parts:
# p1_b = iv (16 B) + p2_B size stored in 3B
# p2_b = file name information + file content + mac
def process_file_to_binary(f_path, k, password):

    
    if os.path.exists(f_path):
        f_name = f_path.rsplit("/")[-1].encode()
        with open(f_path, "rb") as f:
            f_data = f.read()
    else:
        print(f"error: file {f_path} doesn't exist!")
        sys.exit(1)

    data = len(f_name).to_bytes(1) + f_name + f_data
    size = len(data).to_bytes(3)

    plaintext = size + data

    key = hash_digest(password)
    mac = HMAC.new(key, plaintext, SHA256).digest()
    iv, ciphertext = encrypt(plaintext, key)

    p1_B = iv + ciphertext[:3]
    p2_B = ciphertext[3:] + mac

    p1_b = bytes_to_bits(p1_B)
    p1_b = pad_wrap(p1_b,k)

    p2_b = bytes_to_bits(p2_B)
    p2_b = pad_wrap(p2_b,k)

    return p1_b, p2_b



