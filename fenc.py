from Crypto.Cipher import DES
from flask import flash


def save(content, fileType, fileN):
    with open(f'{fileN}.{fileType}', 'wb') as file:
        file.write(content)
    file.close()

def detFileType(file):
    return file.split('.')[-1]

def encr(k, d):
    cipher = DES.new(k.encode(), DES.MODE_ECB)

    with open(d, 'rb') as file:
        data = file.read()
    ext = detFileType(d)
    if len(data) % 8 != 0:
        residue = 8 - int(len(data)%8)
        tta = ' ' * residue
        toCrypt = data + tta.encode()
    else: toCrypt = data

    enc = cipher.encrypt(toCrypt)
    save(enc, ext, './_server_files/docs/encrypted')
    # flash('File encrypted and downloaded!')
    return f'./_server_files/docs/encrypted.{ext}'

def decr(k, d):

    cipher = DES.new(k.encode(), DES.MODE_ECB)
    with open(d, 'rb') as file:
        data = file.read()
    ext = detFileType(d)
    dec = cipher.decrypt(data)
    
    save(dec, ext, './_server_files/docs/decrypted')
    # flash('File decrypted and downloaded!')
    return  f'./_server_files/docs/decrypted.{ext}'