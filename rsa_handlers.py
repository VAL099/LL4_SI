
import random
import math
import base64

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def prime_generator(**kwargs):
    primes = []
    for n in range(kwargs.get('start'), kwargs.get('end')):
        for x in range(2, n):
            if n % x == 0:
                break
        else:
            primes.append(n)
    return primes 

def get2primes(**kwargs):
    primes = prime_generator(start = kwargs.get('start'), end = kwargs.get('end'))
    num1 = random.choice(primes)
    num2 = random.choice(primes)

    return num1, num2

def getKeys(**kwargs):
    p, q = get2primes(start = kwargs.get('start'), end = kwargs.get('end'))
    n = p*q
    phi = (p-1)*(q-1)

    for i in range(0, phi):
        if i > 1 and i < phi and math.gcd(phi, i) == 1:
            e = i
            break
            
    d = pow(e, -1, phi)
    publicKey = f'{e},{n}'
    privateKey = f'{d},{n}'
    return base64.b64encode(publicKey.encode()).decode(), base64.b64encode(privateKey.encode()).decode()

def exportAsFile(data, fn):
    with open(f'./_server_files/docs/{fn}.txt', 'w') as file:
        file.write(data)
        file.close()
    return f'./_server_files/docs/{fn}.txt'

def getPayloadFromFile(fp):
    with open(f'{fp}', 'r') as file:
        payload = file.read()
        file.close()
        print(payload)
    return payload

def sendPrivateKey(receiver, attachement):

    SENDER = 'valeriy13099@gmail.com'
    PASSWORD = 'gvagijjihikvdpkx'

    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = receiver
    msg['Subject'] = 'PRIVATE KEY'
    msg.attach(MIMEText('Genereted on http://192.168.51.154:4587/ \n RSA tools: http://192.168.51.154:4587/rsa'))
    
    attachementFile = open(attachement, 'rb')
    loadFile = MIMEBase('application', 'octate-stream')
    loadFile.set_payload((attachementFile).read())
    encoders.encode_base64(loadFile)
    loadFile.add_header('Content-Disposition', 'attachement', filename = attachement)
    msg.attach(loadFile)
    
    sessionClient = smtplib.SMTP('smtp.gmail.com', 587)
    sessionClient.starttls()
    sessionClient.login(SENDER, PASSWORD)
    txt = msg.as_string()
    sessionClient.sendmail(SENDER, receiver, txt)
    sessionClient.quit()