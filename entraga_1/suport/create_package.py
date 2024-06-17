import hashlib
import struct
def create_package(data, packageSize, packageIndex, packageQuantity):
    message = bytearray() #lista de bytes (mutável)
    message.extend(data[:packageSize]) #pegamos um pacote de tamanho pré-setado
    checksum = hashlib.md5(data).hexdigest() #criamos checksum com o objeto hash do tipo md5
    package_header = struct.pack('!IIII', packageSize, packageIndex, packageQuantity, checksum)
    return package_header + bytearray(message)