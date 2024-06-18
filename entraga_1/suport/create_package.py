import struct
from zlib import crc32
def create_package(data, packageSize, packageIndex, packageQuantity):
    message = bytearray()
    message.extend(data[:packageSize])
    checksum = crc32(data)
    package_header = struct.pack(f'!IIII', packageSize, packageIndex, packageQuantity, checksum)  # Empacota o checksum como bytes
    return package_header + bytearray(message)