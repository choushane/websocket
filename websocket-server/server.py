#!/usr/bin/env python2.7

import os
import string
import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random
import time
import base64
import random
import threading

from websocket_server import WebsocketServer


def show_server_action(client, server):
    server.send_pong(client, "-----------------HELP------------------")
    server.send_pong(client, "'\l'\tShow User List.")
    server.send_pong(client, "---------------------------------------")


def show_user_list(client, server):
    server.send_pong(client, "--------------User List----------------")
    for user in server.get_all_user_name():
        server.send_pong(client, "%s" % user)
    server.send_pong(client, "---------------------------------------")


def auth(code):
    if not os.path.isfile(PRIVATE_KEY):
	return False

    key = RSA.importKey(open(PRIVATE_KEY).read())
    dec = PKCS1_v1_5.new(key)
    try:
        ciphertext = base64.decodestring(code)
        timestamp = dec.decrypt(ciphertext, Random.new().read)
        if int(time.time()) - int(timestamp) < 5:
	    return True
    except:
	return False


def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))


def random_get_name():
    if os.path.isfile(NAME_DICTIONARY):
	return random.choice(open(NAME_DICTIONARY).read().splitlines())
    else:
	return random_char(random.randint(3,6))


def check_display_name(server, display_name, try_count=5):
    if display_name and not server.check_client_recurrent("display_name", display_name):
        return display_name
    else:
	if try_count == 0:
	    return random_char(random.randint(3,6))
	try_count -= 1
        return check_display_name(server, random_get_name(), try_count)


def get_server_time():
    return time.strftime("%H:%M:%S", time.localtime(int(time.time())))


# Called for every client connecting (after handshake)
def new_client(client, server):

    client['display_name'] = check_display_name(server, client['display_name'])

    print("User(%s[%d]) connect. [auth : %r]" % (client['display_name'], client['id'], client['auth']))
    if client['auth'] == True:
	server.send_message_to_all(client, "Enter room.")
	show_user_list(client, server)
    else:
	client['login_time'] = int(time.time())


# Called for every client disconnecting
def client_left(client, server):
    print("%s(%d) disconnected" % (client['display_name'], client['id']))
    if client['auth'] == True:
	server.send_message_to_all(client, "Leave room.")


# Called when a client sends a message
def message_received(client, server, message):
    print("%s(%d): %s" % (client['display_name'], client['id'], message))
    if client['auth'] == True:
	if len(message) > 200:
		message = message[:200]+'..'
	if message == "\l":
	    show_user_list(client, server)
	elif message == "\h":
	    show_server_action(client, server)
	else:
	    server.send_message_to_all(client, "%s[%s]" % (message, get_server_time()))


def ping_received(client, server, message):
    if len(message) > 0 and client['auth'] == False:
        if auth(message):
            client['auth'] = True
	    client['display_name'] = check_display_name(server, client['display_name'])
            new_client(client, server)
	    print("Client %s[%s] auth success." % (client['display_name'], client['address']))
	else:
	    print("Client %s[%s] auth faile." % (client['display_name'], client['address']))
	    server.send_exit(client)
    else:
	server.send_pong(client, message)


def pong_received(client, server, message):
    server.send_pong(client, message)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",default=9001, type=int,
                        help="Server listen port(default:9001)")
    parser.add_argument("-ca", "--ca-file",
                        help="Auth private key.")
    parser.add_argument("-dic", "--name-dictionary",
                        help="Random name dictionary.")

    return parser.parse_args()


def main():
	global PRIVATE_KEY, NAME_DICTIONARY

	args = parse_args()
        disable_auth = True
	print("Server start [%d]" % args.port)

	server = WebsocketServer(args.port)

 	if args.ca_file:
	    print("Private Key : %s" % args.ca_file)
	    PRIVATE_KEY = args.ca_file
	    disable_auth = False
	else:
	    PRIVATE_KEY = ""

	if args.name_dictionary:
	    print("Name Dictionary : %s" % args.name_dictionary)
	    NAME_DICTIONARY = args.name_dictionary
	else:
	    NAME_DICTIONARY = ""

	server.set_disable_auth(disable_auth)
	server.set_fn_new_client(new_client)
	server.set_fn_client_left(client_left)
	server.set_fn_message_received(message_received)
	server.set_fn_ping_received(ping_received)
	server.set_fn_pong_received(pong_received)

	def check_user_status():
	    while True:
		for client in server.get_client_list():
		    if client['auth'] == False and int(time.time()) - client['login_time'] > 5:	
			server.send_exit(client)
		time.sleep(1)

	thread = threading.Thread(target=check_user_status)
	thread.daemon = True
        thread.start()

	server.run_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


