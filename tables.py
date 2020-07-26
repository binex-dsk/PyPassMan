try:
    from sqlalchemy import Table, Column, String, BigInteger, MetaData, create_engine
except:
    print('Please install sqlalchemy with')
    print('python3 -m pip install sqlalchemy')
    exit()

import subprocess

homef = subprocess.Popen('echo ~', shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readline().decode().strip('\n')
engine = create_engine(f'sqlite:///{homef}/passman.db')
meta = MetaData()
conn = engine.connect()
data = Table(
    'data', meta,
    Column('name', String, unique=True),
    Column('description', String),
    Column('password', String, unique=True),
    Column('indices', String),
    Column('iters', String),
    Column('key', BigInteger)
)
master_password = Table(
    'master_password', meta,
    Column('password', String, unique=True)
)
charset = Table(
    'charset', meta,
    Column('set', String),
    Column('key1', BigInteger),
    Column('key2', BigInteger),
    Column('key3', BigInteger),
    Column('key4', BigInteger)
)

meta.create_all(engine)