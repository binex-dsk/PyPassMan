import random, getpass, os, hashlib
import db, encrypt

from tables import conn, data, master_password, charset

print('Welcome to the Python Password Manager!')

exists = db.exists(master_password, {}, conn)
if not exists:
    while True:
        masterpass = getpass.getpass(prompt='Please set a master password '\
        'to unlock your passwords: ')
        if len(masterpass) < 8:
            print("Having a short password is a security risk. "\
            "The shorter the password, the easier it is to guess. "\
            "Please use a length of at least 8 characters.")
            continue
        # hashes the password
        hashed = hashlib.pbkdf2_hmac('sha256', masterpass.encode('utf-8'), b'salt', 100000)

        db.insert(master_password, {'password': hashed}, conn)

        base_set = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`!@#$%^&*()~_+[]\\{\}|;\':",./<>?')
        cset = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`!@#$%^&*()~_+[]\\{\}|;\':",./<>?')
        for x in range(random.randint(10, 13)):
            cset = cset + base_set
            random.shuffle(cset)
        db.insert(charset, {'set': "".join(cset)}, conn)

        os.popen(f'echo {masterpass} > password.txt')
        print('Your master password has been set. I have created a password.txt file '\
        'in the current directory. Please back this up and put it somewhere safe, '\
        'where you can remember where it is but others can\'t access it.')
        break
else:
    while True:
        unlock = getpass.getpass(prompt="Please enter your master password: ")
        hashed = hashlib.pbkdf2_hmac('sha256', unlock.encode('utf-8'), b'salt', 100000)
        if db.exists(master_password, {'password': hashed}, conn):
            print('You may now access your passwords.')
            break
        print('Wrong password.')
while True:
    choice = input("Please choose an option. Type help for options: ")
    if choice == 'help':
        print('add: add a password\ndelete: delete a password\n'\
        'help: this menu\nview: view a password')
    elif choice == 'add':
        while True:
            name = input("What name should this entry have? ")
            if db.exists(data, {'name': name}, conn):
                print('An entry with that name already exists.')
                continue
            break
        description = input("What should be the description of this entry? ")
        while True:
            password = None
            passchoice = input("Do you want to input your own password? ")
            if passchoice == 'yes':
                while True:
                    password = list(getpass.getpass(prompt="Type your password: "))
                    if len(password) < 8:
                        print("Having a short password is a security risk. "\
                        "The shorter the password, the easier it is to guess. "\
                        "Please use a length of at least 8 characters.")
                        continue
                    """if db.exists(data, {'password': password}, conn):
                        print('An entry with that password already exists.\n'\
                        'Using the same password across multiple accounts '\
                        'is a bad idea. Please use a unique password.')
                        continue"""
                    break
            elif passchoice == 'no':
                length = 0
                while True:
                    length = input("What length do you want? ")
                    try:
                        length = int(length)
                    except:
                        print('Please input a number for the length.')
                    if length < 8:
                        print("Having a short password is a security risk. "\
                        "The shorter the password, the easier it is to guess. "\
                        "Please use a length of at least 8 characters.")
                        continue
                    break
                charset = list('abcdefghijklmnopqrstuvwxyz1234567890')
                specialset = list('!@#$%^&*()-_=+,<.>?')
                while True:
                    excluded = input('What special characters do you want to exclude? '\
                    'The current special (non-letter/number) characters included are: '\
                    f'{"".join(specialset)} ')
                    for letter in list(excluded):
                        try:
                            ind = specialset.index(letter)
                            del specialset[ind]
                        except:
                            print(f'Character {letter} not found in special character set.')
                            continue
                    print(f'Final special character set: {"".join(specialset)}')
                    choice = input('Do you want to exclude any more special characters? ')
                    if choice == 'yes':
                        continue
                    break
                while True:
                    included = input('What special characters do you want to add? '\
                    'The current special (non-letter/number) characters included are: '\
                    f'{"".join(specialset)} ')
                    for letter in list(included):
                        try:
                            specialset.index(letter)
                            charset.index(letter)
                            print(f'Character {letter} already in character set.')
                        except:
                            specialset.append(letter)
                            continue
                    print(f'Final special character set: {"".join(specialset)}')
                    choice = input('Do you want to include any more special characters? ')
                    if choice == 'yes':
                        continue
                    break
                capschoice = None
                while True:
                    capschoice = input('Do you want to include capital letters? ')
                    if capschoice == 'yes':
                        charset = charset + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                        break
                    elif capschoice == 'no':
                        break
                    else:
                        print('Please input yes or no.')
                        continue
                fullset = charset + specialset
                print('Generating a random password, please wait...')
                while True:
                    password = random.choices(fullset, k=length)
                    if db.exists(data, {'password': "".join(password)}, conn):
                        continue
                    break
            else:
                print('Please input yes or no.')
                continue
            key = int("".join(random.choices(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], k=14)))
            env = encrypt.encrypt("".join(password), key)
            password = env['code']
            index = env['index']
            db.insert(data, {'name': name, 'description': description, 'password': password, 'indices': index}, conn)
            print(f'Successfully added entry {name}! View it with the view command.')
            break
    elif choice == 'view':
        while True:
            name = input('What entry name do you want to view? Type nothing to view all: ')
            if name == '':
                result = db.fetch(data, {}, conn)
                for row in result:
                    print(row.name)
                break
            entry = db.fetch(data, {'name': name}, conn)
            try:
                entry = entry.fetchone()
            except:
                print('That entry does not exist.')
                continue
            print(f'Name: {entry.name}\nDescription: {entry.description}\n'\
            f'Password: {encrypt.decrypt(entry.password, entry.indices)}')
            break
    elif choice == 'delete':
        while True:
            name = input('What entry do you want to delete? ')
            entry = db.fetch(data, {'name': name}, conn)
            try:
                entry = entry.fetchone()
            except:
                print('That entry does not exist.')
                continue
            db.delete(data, {'name': name}, conn)
            break
    else:
        print('Invalid choice. Please type help to view all commands.')
