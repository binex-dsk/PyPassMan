import random, getpass, string, db

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
        print('add: add a password\ndelete: delete a password\nedit: edit an entry\nview: view a password\ntips: tips for password management\ninfo: some info on passman\nexit: exit out of the program')
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
                while length < 8:
                    length = input("What length do you want? ")
                    try:
                        length = int(length)
                    except:
                        print('Please input a number for the length.')
                        length = 0
                    if length < 8:
                        print("Having a short password is a security risk. "\
                        "The shorter the password, the easier it is to guess. "\
                        "Please use a length of at least 8 characters.")
                        continue
                    break
                charset = list(string.ascii_lowercase + string.digits)
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
                    inc_choice = None
                    while inc_choice not in ('yes', 'no'):
                        inc_choice = input('Do you want to exclude any more special characters? ')
                        if inc_choice not in ('yes', 'no'):
                            print('Please input yes or no.')
                    if inc_choice == 'yes':
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
                    inc_choice = None
                    while inc_choice not in ('yes', 'no'):
                        inc_choice = input('Do you want to include any more special characters? ')
                        if inc_choice not in ('yes', 'no'):
                            print('Please input yes or no.')
                    if inc_choice == 'yes':
                        continue
                    break
                capschoice = None
                while True:
                    capschoice = input('Do you want to include capital letters? ')
                    if capschoice == 'yes':
                        charset += list(string.ascii_uppercase)
                    if capschoice in ('no', 'yes'):
                        break
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
            mp = getmpass()
            db.insert('data', {'name': name, 'description': description, 'password': password})
            db.encrypt(mp[1].encode(), mp[2])
            bpw = password.encode()
            print(f'Successfully added entry {name}! View it with the view command.')
            break
    elif choice == 'view':
        while True:
            name = input('What entry name do you want to view? Type nothing to view all: ')
            if not name:
                for row in c.execute('SELECT name FROM data ORDER BY name'):
                    print(row[0])
                break
            entry = db.fetch('data', {'name': name})
            if not entry:
                print('That entry does not exist.')
                continue
            entry = entry.fetchone()
            print(f'Name: {entry[0]}\nDescription: {entry[1]}\n'\
            f'Password: {entry[2]}')
            break
    elif choice == 'delete':
        while True:
            name = input('What entry do you want to delete? ')
            if not db.exists('data', {'name': name}):
                print('That entry does not exist.')
                continue
            mp = getmpass()
            db.delete('data', {'name': name})
            db.encrypt(mp[1].encode(), mp[2])
            break
        print(f'Successfully deleted entry {name}.')
    elif choice == 'exit':
        print('Thanks for using passman!')
        break
    elif choice == 'tips':
        print('A good password contains:\n- At least 8 characters, but more is always preferred\n- No easy-to-guess phrases or common passwords (See https://github.com/danielmiessler/SecLists/tree/master/Passwords/Common-Credentials)\n- At least one each of a lowercase and uppercase letter, a number, and a special character, but more is always preferred\n- A sequence of characters with no observable pattern (example: things like a1b2c3d4 are generally not preferrable to something like d.Y2/90a)\n- Some sort of meaning that you can use to remember it\nA bad password contains:\n- Less than 8 characters\n- Common, easy-to-guess phrases\n- Sequences of repeated characters or obvious patterns\n- Little variety in the characters\nNever, ever share your passwords. Ever. They are the single most important piece of security in almost everything online. A single person getting your password can cause it to be shared all over the internet, potentially leaking sensitive info.\nIf you can\'t think of a good password, hundreds of tools online can help you with that, including on here.\nChange your password often. Leaks occur often. Remember to occasionally check https://haveibeenpwned.com/ and enter your email to see if your password may have been leaked.\nDo not use the same password for everything. At the very most, use a password on 2 different sites. If someone gets your password and you use the same one for everything, then your accounts will likely be compromised and sensitive info could be leaked.\nDo not store your passwords in an easy-to-find location. Either use a password manager like this one, or store it in a place nobody can find. Never just try to "remember" them, either--your memory is volatile. A password manager is far better at remembering things than you ever will be.\nLock your computer and phone when not using them, especially if you store passwords on it.')
    elif choice == 'info':
        print('Info about passman:\nCreated by: sperg (https://github.com/binex-dsk)\nDiscord ID: 733541115910815755\nPurpose: To provide a simple-to-understand, minimal, and secure password manager.\nRepository: https://github.com/binex-dsk/PyPassMan\nWith significant help from:\nLenny McLennington#3125\nAll issues must be reported to the repository.')
    elif choice == 'edit':
        while True:
            name = input('Which entry would you like to update? Press enter with no input to view all possibilities: ')
            if not name:
                for row in c.execute('SELECT name FROM data ORDER BY name'):
                    print(row[0])
                continue
            entry = db.fetch('data', {'name': name})
            if not entry:
                print('That entry does not exist.')
                continue
            entry = entry.fetchone()
            while True:
                new_name = input('What new name do you want? Type nothing to keep it the same: ') or entry[0]
                if db.exists('data', {'name': name}):
                    print('An entry with that name already exists.')
                    continue
                break
            new_desc = input('What new description do you want? Type nothing to keep it the same: ') or entry[1]
            while True:
                new_pass = getpass.getpass(prompt='What new password do you want? Type nothing to keep it the same: ') or entry[2]
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
            mp = getmpass()
            db.update('data', {'name': entry[0]}, {'name': new_name, 'description': new_desc, 'password': new_pass})
            db.encrypt(mp[1].encode(), mp[2])
            print(f'Successfully edited entry {name}.')
            break
    else:
        print('Invalid choice. Please type help to view all commands.')
