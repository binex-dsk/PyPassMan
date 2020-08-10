# pylint: disable=unused-variable
import hashlib, base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from tables import conn, c
q = '"'
def exists(table, vals):
    ex = c.execute(f'SELECT * FROM {table} WHERE {" AND ".join([f"{t[0]}={q}{t[1]}{q}" for t in list(vals.items())])}').fetchone()
    return bool(ex)

def insert(table, vals):
    c.execute(f'INSERT INTO {table} ({", ".join(list(vals.keys()))}) VALUES ({", ".join([f"{q}{x}{q}" for x in list(vals.values())])})')
    conn.commit()

def delete(table, vals):
    if not exists(table, vals):
        raise Exception('Row not found.')
    c.execute(f'DELETE FROM {table} WHERE {" AND ".join([f"{t[0]}={q}{t[1]}{q}" for t in list(vals.items())])}')
    conn.commit()

def fetch(table, vals):
    if not exists(table, vals):
        return None
    ex = c.execute(f'SELECT * FROM {table} WHERE {" AND ".join([f"{t[0]}={q}{t[1]}{q}" for t in list(vals.items())])}')
    return ex

def update(table, vals, newvals):
    if not exists(table, vals):
        raise Exception('Row not found.')
    vs = list(vals.items())
    nvs = list(newvals.items())
    exec_str = f"UPDATE {table} SET "
    nvlist = []
    vlist = []
    for nv in nvs:
        nvlist.append(f'{nv[0]}="{nv[1]}"')
    exec_str += f"{', '.join(nvlist)} WHERE "
    for v in vs:
        vlist.append(f'{v[0]} = "{v[1]}"')
    exec_str += ', '.join(vlist)
    c.execute(exec_str)
    conn.commit()

def encrypt(key, iv):
    data = b""
    for line in conn.iterdump():
        data += f"{line}\n".encode()

    padder = PKCS7(256).padder()
    pkey = padder.update(key) + padder.finalize()
    padder = PKCS7(1024).padder()
    pdata = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(pkey), modes.CBC(iv), backend=default_backend())
    enc = cipher.encryptor()
    ct = enc.update(pdata) + enc.finalize()
    to_write = f"{base64.b64encode(iv).decode()}\n{hashlib.sha256(ct).hexdigest()}\n".encode()
    to_write += ct
    homef = str(Path.home())
    pdb = open(f'{homef}/passman.pdb', 'wb+')
    pdb.write(to_write)
