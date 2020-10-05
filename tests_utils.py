from random import getrandbits
from binascii import unhexlify

def create_random_hex_file(num_bytes, filename):
    with open(filename, "wb") as file:
        rand_bytes = getrandbits(8 * num_bytes)
        hex_dump = hex(rand_bytes)[2:]
        file.write(unhexlify(hex_dump))
