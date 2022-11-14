import OpenSSL
from PDFNetPython3.PDFNetPython import *
import datetime, random, handlers

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import flash

stamp = datetime.datetime.now() #  str(stamp).split('.')[0]

def keygen():
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 4096)
    return key

def create_digital_certificate(**kwargs):
    certificate = OpenSSL.crypto.X509()
    certificate.get_subject().CN = kwargs.get('user').upper()
    certificate.set_serial_number(4587)
    certificate.gmtime_adj_notBefore(0)
    certificate.gmtime_adj_notAfter(1 * 365 * 24 * 60 * 60) # 1 year in seconds this is expiration date
    certificate.set_issuer((certificate.get_subject()))
    certificate.set_pubkey(kwargs.get('key'))
    certificate.sign(kwargs.get('key'), 'sha256')
    return certificate

def certgen(**kwargs):
    summary = {}
    summary['OpenSSL Version'] = OpenSSL.__version__
    path1 = './_server_files/trash'
    path = './_server_files/certificates'
    username = kwargs.get('u')
    user = handlers.dbHandler(op_type = 'get_user', u = username)

    k = keygen()
    # private key
    with open(f'{path1}/private_key_{username}.pem', 'wb') as private_key:
        pk = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, k)
        private_key.write(pk)
    # certificate
    certificate = create_digital_certificate(key = k, user = user)
    with open(f'{path}/{username}_public_certificate.cer', 'wb') as c:
        certif = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
        c.write(certif)
    # public key
    with open(f'{path1}/public_key_{username}.pem', 'wb') as public_key:
        pbK = OpenSSL.crypto.dump_publickey(
            OpenSSL.crypto.FILETYPE_PEM, certificate.get_pubkey())
        public_key.write(pbK)
    
    # Adobe Certificate
    p12 = OpenSSL.crypto.PKCS12()
    p12.set_privatekey(k)
    p12.set_certificate(certificate)
    open(f'{path}/{username}_private_certificate.pfx', 'wb').write(p12.export())
    handlers.rm_trash(f'{path1}/public_key_{username}.pem'), handlers.rm_trash(f'{path1}/private_key_{username}.pem')
    # add_readme(u = user, p = path)

def sign(**kwargs): 
    
    PDFNet.Initialize('demo:1667230704947:7aac474d03000000001f023612cc221e0273f4b0d1ee33c13780314c46')
    document  = PDFDoc(kwargs.get('f'))
    sign_field = SignatureWidget.Create(
        document, Rect( 150, 250, 150 + 100, 250 + 100), kwargs.get('id'))

    pg = document.GetPage(kwargs.get('p'))
    pg.AnnotPushBack(sign_field)

    sign = kwargs.get('sign')
    certificate = kwargs.get('c')

    approval_field = document.GetField(kwargs.get('id'))
    approval_signature_digsig_field = DigitalSignatureField(approval_field)
    img = Image.Create(document.GetSDFDoc(), sign)
    found_approval_signature_widget = SignatureWidget(approval_field.GetSDFObj())
    found_approval_signature_widget.CreateSignatureAppearance(img)

    approval_signature_digsig_field.SignOnNextSave(certificate, '')
    document.Save(kwargs.get('path'), SDFDoc.e_incremental)

    return flash('Signed')

def add_readme(**kwargs):
    payload = f"""
    HI, {kwargs.get('u')}!
    Steps to use this:

    1. Open Adobe Reader
    2. On the top panel: Edit -> Preferences
    3. Select Signatures then Identities & Trusted Certificates 
    4. Press " More... " button
    5. In the meniu that appeared select " Trusted Certificates "
    6. Import the .cer file and mark it as a trusted root. (Google Search if need ;) )
    
    After this steps Adobe Reader will know that your certificate used for signing this document is the valid one!
    """
    with open(f'{kwargs.get("p")}/README.txt', 'w') as f:
        f.write(payload)
        f.close()

def send(**kwargs):

    SENDER = 'valeriy13099@gmail.com'
    PASSWORD = 'gvagijjihikvdpkx'

    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = kwargs.get('recv')
    msg['Subject'] = 'PRIVATE KEY'
    msg.attach(MIMEText('Signed on http://127.0.0.1:4587/dsa_sign'))
    
    attachementFile = open(kwargs.get('file'), 'rb')
    loadFile = MIMEBase('application', 'octate-stream')
    loadFile.set_payload((attachementFile).read())
    encoders.encode_base64(loadFile)
    loadFile.add_header('Content-Disposition', 'attachement', filename = kwargs.get('file'))
    msg.attach(loadFile)
    
    sessionClient = smtplib.SMTP('smtp.gmail.com', 587)
    sessionClient.starttls()
    sessionClient.login(SENDER, PASSWORD)
    txt = msg.as_string()
    sessionClient.sendmail(SENDER, kwargs.get('recv'), txt)
    sessionClient.quit()