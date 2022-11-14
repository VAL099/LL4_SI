import hashlib, sqlite3, os
from flask import flash

connection = sqlite3.connect('./_server_files/db/storage.db', check_same_thread = False)
cursor = connection.cursor()  

def dbHandler(**kwargs):
    operation_type = kwargs.get('op_type')

    username = kwargs.get('u')
    password = kwargs.get('p')
    name = kwargs.get('n')
    surname = kwargs.get('s')

    private_certificate = kwargs.get('pr')
    public_certificate = kwargs.get('pb')
    signature = kwargs.get('sg')
    
    if operation_type == 'add_user':
        cursor.execute("""
        INSERT INTO users(username, password, name, surname) values (?, ?, ?, ?)""",(username,password,name,surname))
        connection.commit()
        return flash('Your registration passed succesfully!')
    elif operation_type == 'check_user':
        pswd = hashlib.sha256(password.encode()).hexdigest()
        data = cursor.execute('SELECT password FROM users where username = ?', (username,)).fetchall()
        try:
            if data[0][0] == pswd: return True
            else: flash('Wrong Credentials!!!', 'error')
        except IndexError: return flash('Unexisting user!!!', 'error')
    elif operation_type == 'add_certificate':
        cursor.execute("""
        INSERT INTO signatures(public_certificate, private_certificate, signature, username) values (?, ?, ?, ?)""",
            (public_certificate, private_certificate, signature, username))
        connection.commit()
        return flash('Signature created and registered')
    elif operation_type == 'get_user':
        data = cursor.execute('SELECT name, surname FROM users where username = ?', (username,)).fetchall()
        user = data[0][0] + ' ' + data[0][1]
        return user
    elif operation_type == 'get_priv_cert':
        data = cursor.execute('SELECT public_certificate FROM signatures where username = ?', (username, )).fetchall()
        bin2file(f'./_server_files/signatures/{username}_public_certificate.cer', data[0][0])
        return f'./_server_files/signatures/{username}_public_certificate.cer'
    elif operation_type == 'get_signatures':
        data = cursor.execute('SELECT private_certificate, signature FROM signatures where username = ?', (username, )).fetchall()
        bin2file(f'./_server_files/signatures/{username}_signature.png', data[0][1])
        bin2file(f'./_server_files/certificates/{username}_certificate.pfx', data[0][0])
        return f'./_server_files/signatures/{username}_signature.png', f'./_server_files/certificates/{username}_certificate.pfx'
    elif operation_type == 'register_keys':
        cursor.execute('INSERT INTO rsa_keys(first_key, first_user, second_key, second_user) values (?, ?, ?, ?)',
        (kwargs.get('key1'), kwargs.get('user1'), kwargs.get('key2'), kwargs.get('user2')))
        connection.commit()
        return flash('Keys registered!')
    elif operation_type == 'get_public_key':
        data = cursor.execute('SELECT first_key FROM rsa_keys where first_user = ? and second_user = ?', (username, kwargs.get("coUser"))).fetchall()
        return data[0][0]
    elif operation_type == 'get_private_key':
        data = cursor.execute('SELECT second_key FROM rsa_keys where second_user = ? and first_user = ?', (username, kwargs.get("coUser"))).fetchall()
        return data[0][0]

def file2bin(fp):
    with open(fp, 'rb') as file:
        data = file.read()
    return data

def bin2file(fp, data):
    file = open(fp, 'wb')
    file.write(data)
    file.close

def rm_trash(fp):
    if os.path.exists(fp):
        os.remove(fp)

def signed_file(**kwargs):
    username = kwargs.get('u')