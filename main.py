from flask import Flask, render_template, session, request, redirect, url_for, flash, send_file
import hashlib
from handlers import *
from dsa_utils import certgen, sign
import create_signature, fenc, rsa, rsa_handlers

app = Flask(__name__)
app.secret_key = '6523e58bc0eec42c31b9635d5e0dfc23b6d119b73e633bf3a5284c79bb4a1ede'

@app.route('/')
def home_page():
    if 'user' in session:
        username = session['user']
        flash(f'Welcome, {username}!', 'info')
        return render_template('index.html', param = 1)
    else: return render_template('index.html', param = 0)

@app.route('/signIn', methods = ['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['passwd']
        if dbHandler(u = username, p = password, op_type = 'check_user') == True:
            session['user'] = username # create a session
            return redirect(url_for('home_page'))
        else:
            return render_template('sign_in.html')
    else:
        return render_template('sign_in.html')

@app.route('/signUp', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['uname']
        password = hashlib.sha256(request.form['passwd'].encode()).hexdigest() # hashed password
        name = request.form['first_name']
        surname = request.form['last_name']
        dbHandler(u = username, p = password, n = name, s = surname, op_type = 'add_user')
        session['user'] = username
        return redirect(url_for('home_page'))
    else: return render_template('sign_up.html')

@app.route('/signOut')
def sign_out():
    if 'user' in session:
        session.pop('user')
        flash("You've been logged out!")
        return redirect(url_for('home_page'))
    else:
        flash("You should firsly SignIn!")
    return redirect(url_for('home_page'))

@app.route('/certificate_generation')
def certificate_generator():
    if 'user' in session:
        certgen(u = session['user'])
        ns = dbHandler(op_type = 'get_user', u = session['user'])
        create_signature.create(n = ns.split(' ')[0], s = ns.split(' ')[1], u = session['user'])

        file1 = f'./_server_files/certificates/{session["user"]}_private_certificate.pfx'
        file2 = f'./_server_files/certificates/{session["user"]}_public_certificate.cer'
        file3 = f'./_server_files/signatures/{session["user"]}_signature.png'

        dbHandler(op_type = 'add_certificate', pr = file2bin(file1), pb = file2bin(file2), sg = file2bin(file3), u = session['user'])
        rm_trash(file1), rm_trash(file2), rm_trash(file3)
        return render_template('eSign_menu.html', param = 1)
    else: 
        flash('You should firstly Sign In!')
        return render_template('eSign_menu.html', param = 0)

@app.route('/get_public_certificate')
def get_private_ceritifcate():
    if 'user' in session:
            certificate = dbHandler(op_type = 'get_priv_cert', u = session['user'])
            return send_file(certificate, as_attachment = True)
    else: 
        flash('You should firstly Sign In!')
        return render_template('eSign_menu.html', param = 0)

@app.route('/eSign', methods = ['GET', 'POST'])
def sign_document():
    if 'user' in session:
        if request.method == 'POST':
            if 'user' in session:
                file = request.files['file']
                page = request.form['pg']
                fn = file.filename
                file.save(f'./_server_files/docs/{session["user"]}_{fn}')
                eSign, eCertificate = dbHandler(op_type = 'get_signatures', u = session['user'])
                save_to = f'./_server_files/docs/{session["user"]}_signed.pdf'
                file_to_sign = f'./_server_files/docs/{session["user"]}_{fn}'
                sign(f = file_to_sign, p = int(page), id = 'eSign099', sign = eSign, c = eCertificate, path = save_to)
                flash('Signed!')
                rm_trash(eSign), rm_trash(eCertificate), rm_trash(f'./_server_files/docs/{session["user"]}_{fn}')
                return send_file(save_to, as_attachment = True)
            else: flash('You should firstly Sign In!')
        return render_template('eSign_menu.html', param = 1)
    else: 
        return render_template('eSign_menu.html', param = 0)

@app.route('/share_files', methods = ['GET', 'POST'])
def share_file():
    if 'user' in session:
        if request.method == 'POST':
            if 'user' in session:
                if request.form.get('encode'):
                    file = request.files['file']
                    key = request.form['key']
                    fn = file.filename
                    file.save(f'./_server_files/trash/{session["user"]}_{fn}')
                    encr_loc = fenc.encr(key, f'./_server_files/trash/{session["user"]}_{fn}')
                    # flash('File encrypted and downloaded!')
                    return send_file(encr_loc, as_attachment = True)
                elif request.form.get('decode'):
                    file = request.files['file']
                    key = request.form['key']
                    fn = file.filename
                    file.save(f'./_server_files/trash/{session["user"]}_{fn}')
                    encr_loc = fenc.decr(key, f'./_server_files/trash/{session["user"]}_{fn}')
                    return send_file(encr_loc, as_attachment = True)
            else: flash('You should firstly Sign In!')
        return render_template('share_files.html', param = 1)
    else: 
        return render_template('share_files.html', param = 0)

@app.route('/encrypt_data', methods = ['GET', 'POST'])
def rsa_work():
    if 'user' in session:
        if request.method == 'POST':
            if 'user' in session:
                if request.form.get('keygen'):
                    key1, key2 = rsa_handlers.getKeys(start = 10000, end = 100000)
                    print(key1)
                    print(key2)
                    first_user = session['user']
                    second_user = request.form['userPair']
                    dbHandler(op_type = 'register_keys', key1 = key1, user1 = first_user, key2 = key2, user2 = second_user)
                elif request.form.get('encrypt'):
                    file = request.files['file']
                    coUsr = request.form['pair_user']
                    fn = file.filename
                    file.save(f'./_server_files/trash/{session["user"]}_{fn}')
                    data = rsa_handlers.getPayloadFromFile(f'./_server_files/trash/{session["user"]}_{fn}')
                    key = dbHandler(op_type = 'get_public_key', u = session['user'], coUser = coUsr)
                    enc_data = rsa.encr(data, key)
                    encrFile = rsa_handlers.exportAsFile(enc_data, f'crypted_by_{session["user"]}')
                    return send_file(encrFile, as_attachment = True)
                elif request.form.get('decrypt'):
                    file = request.files['file']
                    coUsr = request.form['pair_user']
                    fn = file.filename
                    file.save(f'./_server_files/trash/{session["user"]}_{fn}')
                    data = rsa_handlers.getPayloadFromFile(f'./_server_files/trash/{session["user"]}_{fn}')
                    key = dbHandler(op_type = 'get_private_key', u = session['user'], coUser = coUsr)
                    decr_data = rsa.decr(data, key)
                    encrFile = rsa_handlers.exportAsFile(decr_data, f'decrypted_by_{session["user"]}')
                    return send_file(encrFile, as_attachment = True)
            flash('You should firstly Sign In!')
            return render_template('rsa.html', param = 0)
        return render_template('rsa.html', param = 1)
    else:
        return render_template('rsa.html', param = 0)

if __name__ == '__main__':
    app.run(debug = True, host = '127.0.0.1', port = 4587)