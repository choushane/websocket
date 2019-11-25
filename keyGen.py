#!/usr/bin/env python2.7
#coding=utf-8

from Crypto.PublicKey import RSA

rsa = RSA.generate(1024)

privatekey = rsa.exportKey()
with open('privatekey.pem', 'w') as f:
    f.write(privatekey)

publickey = rsa.publickey().exportKey()
with open('publickey.pem', 'w') as f:
    f.write(publickey)
