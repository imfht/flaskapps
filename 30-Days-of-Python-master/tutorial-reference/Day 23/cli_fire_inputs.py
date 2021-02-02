from getpass import getpass
import fire

def login(name=None):   
    if name == None:
        name = input("What's your name?\n")
    pw = getpass("What's your password?\n")
    return name, pw

if __name__ == '__main__':
    fire.Fire(login)
