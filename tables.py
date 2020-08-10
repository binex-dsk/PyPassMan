from sqlite3 import connect
import hashlib, os, getpass, base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
import db

conn = connect(':memory:')
c = conn.cursor()
homef = str(Path.home())
iv = None
def run():
    pdb = os.path.exists(f'{homef}/passman.pdb')
    if pdb:
        prd = getmpass(txt=' to login')[0]
        c.executescript(prd.decode())
    else:
        iv = os.urandom(16)
        psw = getpass.getpass('Welcome to passman!\nTo start, please create a master password: ')
        c.execute('CREATE TABLE data (name text, description DEFAULT "No description provided", password text)')
        conn.commit()
        db.encrypt(psw.encode(), iv)
        print('Successfully set master password.\nIt is HIGHLY important that you keep this in a safe place. Without the password, there is literally no way to access your data!')

def getmpass(txt=" to confirm this"):
    pdb = open(f'{homef}/passman.pdb', 'rb')
    iv = base64.b64decode(pdb.readline().strip(b'\n'))
    hash = pdb.readline().strip(b'\n')
    r = pdb.read()
    while True:
        pw = getpass.getpass(f'Please enter your master password{txt}: ')

        padder = PKCS7(256).padder()
        ppw = padder.update(pw.encode()) + padder.finalize()

        cipher = Cipher(algorithms.AES(ppw), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        rd = dec.update(r) + dec.finalize()
        padder = PKCS7(1024).unpadder()
        try:
            prd = padder.update(rd) + padder.finalize()
        except:
            print('Wrong password, try again.')
            continue

        if hash == hashlib.sha256(r).hexdigest().encode():
            break
        print('Wrong password, try again.')
    return prd, pw, iv
