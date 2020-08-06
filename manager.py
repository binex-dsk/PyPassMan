import random, getpass, os
import db

import tables
from tables import c, getmpass

tables.run()
print('You have now entered passman.\n'\
    'The source code can be found at https://github.com/binex-dsk/PyPassMan.\n'\
    'Please report any bugs you find there.\n'\
    'For available commands, type help.')
while True:
    choice = input("passman> ")
    if choice == 'help':
        print('add: add a password\ndelete: delete a password\n'\
        'help: this menu\nview: view a password\n'\
        'exit: exit out of the program')
    elif choice == 'add':
        while True:
            name = input("What name should this entry have? ")
            if db.exists('data', {'name': name}):
                print('An entry with that name already exists.')
                continue
            break
        description = input("What should be the description of this entry? ")
        while True:
            password = None
            passchoice = input("Do you want to input your own password? ")
            if passchoice == 'yes':
                while True:
                    password = getpass.getpass(prompt="Type your password: ")
                    if len(password) < 8:
                        print("Having a short password is a security risk. "\
                        "The shorter the password, the easier it is to guess. "\
                        "Please use a length of at least 8 characters.")
                        continue
                    if db.exists('data', {'password': password}):
                        print('An entry with that password already exists.\n'\
                        'Using the same password across multiple accounts '\
                        'is a bad idea. Please use a unique password.')
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
                    password = ''.join(random.choices(fullset, k=length))
                    if db.exists('data', {'password': password}):
                        continue
                    break
            else:
                print('Please input yes or no.')
                continue
            mp = getmpass(txt=' to confirm this')
            db.insert('data', {'name': name, 'description': description, 'password': password})
            db.encrypt(mp[1].encode(), mp[2])
            iv = os.urandom(16)
            bpw = password.encode()
            print(f'Successfully added entry {name}! View it with the view command.')
            break
    elif choice == 'view':
        while True:
            name = input('What entry name do you want to view? Type nothing to view all: ')
            if name == '':
                for row in c.execute('SELECT name FROM data ORDER BY name'):
                    print(row[0])
                break
            entry = db.fetch('data', {'name': name}).fetchone()
            if not entry:
                print('That entry does not exist.')
                continue
            print(f'Name: {entry[0]}\nDescription: {entry[1]}\n'\
            f'Password: {entry[2]}')
            break
    elif choice == 'delete':
        while True:
            name = input('What entry do you want to delete? ')
            if not db.exists('data', {'name': name}):
                print('That entry does not exist.')
                continue
            db.delete('data', {'name': name})
            break
    elif choice == 'exit':
        print('Thanks for using passman!')
        exit(0)
    else:
        print('Invalid choice. Please type help to view all commands.')
