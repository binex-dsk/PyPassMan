import random, getpass, os, hashlib
from db import *
from encrypt import *

from tables import conn, data, master_password, charset

print('Welcome to the Python Password Manager!')

existss = exists(master_password, {}, conn)
if not existss:
    while True:
        masterpass = getpass.getpass(prompt='Welcome to the Python Password Manager!\nPlease set a master password '
                                     'to unlock your passwords: ')
        if len(masterpass) < 8:
            print("Having a short password is a security risk. "
                  "The shorter the password, the easier it is to guess. "
                  "Please use a length of at least 8 characters.")
            continue
        # hashes the password
        hashed = hashlib.pbkdf2_hmac(
            'sha256', masterpass.encode('utf-8'), b'salt', 100000)

        insert(master_password, {'password': hashed}, conn)

        base_set = list(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`!@#$%^&*()~_+[]\\{\}|;\':",./<>?')
        cset = list(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`!@#$%^&*()~_+[]\\{\}|;\':",./<>?')
        for x in range(random.randint(10, 13)):
            cset = cset + base_set
            random.shuffle(cset)
        keys = []
        for x in range(4):
            keys.append(random.randint(1000000000, 9999999999))
        insert(charset, {'set': "".join(
            cset), 'key1': keys[0], 'key2': keys[1], 'key3': keys[2], 'key4': keys[3]}, conn)

        os.popen(f'echo {masterpass} > password.txt')
        print('Your master password has been set. I have created a password.txt file '
              'in the current directory. Please back this up and put it somewhere safe, '
              'where you can remember where it is but others can\'t access it.')
        break
else:
    while True:
        unlock = getpass.getpass(prompt="Please enter your master password: ")
        hashed = hashlib.pbkdf2_hmac(
            'sha256', unlock.encode('utf-8'), b'salt', 100000)
        if exists(master_password, {'password': hashed}, conn):
            break
        print('Wrong password.')
print('Welcome to the Python Password Manager.\n'
      'The source code can be found at https://github.com/binex-dsk/PyPassMan.\n'
      'Please redirect any bugs you find to there.\n'
      'For available commands, type help.')
while True:
    choice = input("passman> ")
    if choice == 'help':
        print('add: add a password\ndelete: delete a password\n'
              'help: this menu\nview: view a password\nexit: exit out of the program')
    elif choice == 'add':
        while True:
            name = input("What name should this entry have? ")
            if exists(data, {'name': name}, conn):
                print('An entry with that name already exists.')
                continue
            break
        description = input("What should be the description of this entry? ")
        while True:
            password = None
            passchoice = input("Do you want to input your own password? ")
            if passchoice == 'yes':
                while True:
                    password = list(getpass.getpass(
                        prompt="Type your password: "))
                    if len(password) < 8:
                        print("Having a short password is a security risk. "
                              "The shorter the password, the easier it is to guess. "
                              "Please use a length of at least 8 characters.")
                        continue
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
                        print("Having a short password is a security risk. "
                              "The shorter the password, the easier it is to guess. "
                              "Please use a length of at least 8 characters.")
                        continue
                    break
                charsset = list('abcdefghijklmnopqrstuvwxyz1234567890')
                specialset = list('!@#$%^&*()-_=+,<.>?')
                while True:
                    excluded = input('What special characters do you want to exclude? '
                                     'The current special (non-letter/number) characters included are: '
                                     f'{"".join(specialset)} ')
                    for letter in list(excluded):
                        try:
                            ind = specialset.index(letter)
                            del specialset[ind]
                        except:
                            print(
                                f'Character {letter} not found in special character set.')
                            continue
                    print(
                        f'Final special character set: {"".join(specialset)}')
                    choice = input(
                        'Do you want to exclude any more special characters? ')
                    if choice == 'yes':
                        continue
                    break
                while True:
                    included = input('What special characters do you want to add? '
                                     'The current special (non-letter/number) characters included are: '
                                     f'{"".join(specialset)} ')
                    for letter in list(included):
                        try:
                            specialset.index(letter)
                            charsset.index(letter)
                            print(
                                f'Character {letter} already in character set.')
                        except:
                            specialset.append(letter)
                            continue
                    print(
                        f'Final special character set: {"".join(specialset)}')
                    choice = input(
                        'Do you want to include any more special characters? ')
                    if choice == 'yes':
                        continue
                    break
                capschoice = None
                while True:
                    capschoice = input(
                        'Do you want to include capital letters? ')
                    if capschoice == 'yes':
                        charsset = charsset + \
                            list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                        break
                    elif capschoice == 'no':
                        break
                    else:
                        print('Please input yes or no.')
                        continue
                fullset = charsset + specialset
                print('Generating a random password, please wait...')
                while True:
                    password = random.choices(fullset, k=length)
                    if exists(data, {'password': "".join(password)}, conn):
                        continue
                    break
            else:
                print('Please input yes or no.')
                continue
            key = int("".join(random.choices(
                ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], k=14)))
            env = encrypt("".join(password), key)
            password = env['code']
            index = env['index']
            iters = env['iters']
            insert(data, {'name': name, 'description': description,
                          'password': password, 'indices': index, 'iters': iters, 'key': key}, conn)
            print(
                f'Successfully added entry {name}! View it with the view command.')
            break
    elif choice == 'view':
        while True:
            name = input(
                'What entry name do you want to view? Type nothing to view all: ')
            if name == '':
                result = fetch(data, {}, conn)
                for row in result:
                    print(row.name)
                break
            entry = fetch(data, {'name': name}, conn)
            try:
                entry = entry.fetchone()
            except:
                print('That entry does not exist.')
                continue
            print(f'Name: {entry.name}\nDescription: {entry.description}\n'
                  f'Password: {decrypt(entry.password, entry.indices, entry.iters, entry.key)}')
            break
    elif choice == 'delete':
        while True:
            name = input('What entry do you want to delete? ')
            entry = fetch(data, {'name': name}, conn)
            try:
                entry = entry.fetchone()
            except:
                print('That entry does not exist.')
                continue
            delete(data, {'name': name}, conn)
            break
    elif choice == 'exit':
        print('Thanks for using the Python Password Manager!')
        exit(0)
    else:
        print('Invalid choice. Please type help to view all commands.')
