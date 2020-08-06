from sqlite3 import connect
import hashlib, os, random, string, getpass
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
import db

#conn = connect('data.db')
conn = connect(':memory:')
c = conn.cursor()
homef = str(Path.home())
iv = None
def run():
    pdb = os.path.exists(f'{homef}/passman.pdb')
    if pdb:
        prd = getmpass()[0]
        c.executescript(prd.decode())
    else:
        iv = ''.join(random.choices(string.ascii_letters, k=16)).encode()
        psw = input('Welcome to passman!\nTo start, please create a master password: ')
        #cipher = Cipher(algorithms.AES(psw.encode()), modes.CBC(iv), backend=default_backend())
        c.execute('CREATE TABLE data (name text, description DEFAULT "No description provided", password text)')
        conn.commit()
        db.encrypt(psw.encode(), iv)
        print('Successfully set master password.')

def getmpass(txt=""):
    pdb = open(f'{homef}/passman.pdb', 'rb')
    iv = pdb.readline().strip(b'\n').replace(b"b'", b'').replace(b"'", b'')
    hash = pdb.readline().strip(b'\n').replace(b"b'", b'').replace(b"'", b'')
    r = pdb.read()
    while True:
        pw = getpass.getpass(f'Please enter your master password{txt}: ')

        padder = PKCS7(256).padder()
        ppw = padder.update(pw.encode()) + padder.finalize()

        cipher = Cipher(algorithms.AES(ppw), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        rd = dec.update(r) + dec.finalize()
        padder = PKCS7(1024).unpadder()
        prd = padder.update(rd) + padder.finalize()

        if hash == hashlib.sha256(r).hexdigest().encode():
            break
        print('Wrong password, try again.')
    return prd, pw, iv
