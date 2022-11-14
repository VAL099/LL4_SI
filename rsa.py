
import os; os.system('cls')
import math
import base64
import random
import rsa_handlers

def encr(data, k):
    
    temp = []
    for character in data:
        temp.append( ord(character) )
    # key
    key = base64.b64decode(k.encode()).decode().split(',')
    # chiphering
    ciphered = ''
    for block in temp:
        ciphered += str( pow(int(block), int(key[0]), int(key[1]) ) ) + '|' 
    ciphered = base64.b64encode(ciphered.encode()).decode() # serialising to base64
    return ciphered 

def decr(data, k):
    
    toDecr = base64.b64decode(data.encode()).decode().split('|'); toDecr.pop() # deserialising from base64
    for i in range (0, len(toDecr)):
        toDecr[i] = int(toDecr[i]) # convert all elements to int
    # key
    key = base64.b64decode(k.encode()).decode().split(',')
    
    # unchiphering
    temp = []
    for block in toDecr:
        temp.append( pow( block, int(key[0]), int(key[1]) ) )
    unciphered = ''
    for element in temp:
        unciphered += chr(element)
    return unciphered

# encrypted = encr('HeLL0 WoRlD', 'MywzMTIzNjQwOQ==')
# print(f'encrypted: {encrypted}')
# decrypted = decr(encrypted, 'MjA4MTY4MTEsMzEyMzY0MDk=')
# print(f'decrypted: {decrypted}')
