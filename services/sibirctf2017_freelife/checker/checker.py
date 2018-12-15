#!/usr/bin/python

import os
import requests
import random
from sys import argv


PORT=8000


def check(hostname):
    try:
        response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
        if response != 0:
            print("Host unreachable")
            return(104)
        r = requests.get('http://'+hostname+':'+PORT)
        if "<title>Free Life</title>" not in r.text:
            print("'Free Life' in title not found")
            return(104)
        print("Ok")
        return(101)
    except:
        print("%s", str(e))
        return(104)


def put(hostname, id, flag):
    try:
        phone = "+7 %d%d%d %d%d%d %d%d %d%d" % tuple(random.randint(0,9)
                                         for _ in range(10))
        data = {
            "name":id,
            "email":"user_%s@trusty.mail" % id,
            "address":"Solar system",
            "phone":phone,
            "ccn":flag}

        r = requests.post(
            "http://%s:%d/contact" % (hostname, PORT), 
            data = data)
        ans = 'CONTACT US'

        if ans in r.text:
            print("Ok")
            return(101)
        else:
            print("Not found 'CONTACT US'")
            return(103)

    except Exception as e:
        print("%s", str(e))
        return(104)


def get(hostname, id, flag):
    try:
        data = {
            "name":id,
            "email":"user_%s@trusty.mail" % id,
            "address":"Solar system",
            "phone":"tyc",
            "ccn":"tyc"}
        r = requests.post(
            "http://%s:%d/contact" % (hostname, PORT), 
            data = data)

        if flag in r.text:
            print("Ok")
            return(101)
        else:
            print("Flag is not found")
            return(104)
    except Exception as e:
        print("%s", str(e))
        return(104)

        
if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == "check":
            if len(argv) > 2:
                exit(check(argv[2]))
        elif argv[1] == "put":
            if len(argv) > 4:
                exit(put(argv[2], argv[3], argv[4]))
        elif argv[1] == "get":
            if len(argv) > 4:
                exit(get(argv[2], argv[3], argv[4]))
    exit(110)

