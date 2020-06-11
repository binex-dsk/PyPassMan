try:
    from sqlalchemy import Table, Column, String, MetaData, create_engine
except:
    print('Please install sqlalchemy with')
    print('python3 -m pip install sqlalchemy')
    exit()
engine = create_engine('sqlite:///data.db')
meta = MetaData()
conn = engine.connect()

data = Table(
    'data', meta,
    Column('name', String, unique=True),
    Column('description', String),
    Column('password', String, unique=True),
    Column('indices', String)
)
master_password = Table(
    'master_password', meta,
    Column('password', String, unique=True)
)
charset = Table(
    'charset', meta,
    Column('set', String)
)

meta.create_all(engine)
