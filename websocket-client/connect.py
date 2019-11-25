#!/usr/bin/env python2.7

import argparse
import code
import sys
import threading
import time

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

import six
from six.moves.urllib.parse import urlparse

import websocket
import base64

try:
    import readline
except ImportError:
    pass


def get_encoding():
    encoding = getattr(sys.stdin, "encoding", "")
    if not encoding:
        return "utf-8"
    else:
        return encoding.lower()


OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
ENCODING = get_encoding()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", metavar="ws_url",
                        help="websocket url. ex. ws://127.0.0.1:8888/")
    parser.add_argument("-d", "--display_name",
                        help="User display name")
    parser.add_argument("-ca", "--ca-file",
                        help="Auth server public key.")
    return parser.parse_args()


class RawInput:

    def raw_input(self, prompt):
        if six.PY3:
            line = input(prompt)
        else:
            line = raw_input(prompt)

        if ENCODING and ENCODING != "utf-8" and not isinstance(line, six.text_type):
            line = line.decode(ENCODING).encode("utf-8")
        elif isinstance(line, six.text_type):
            line = line.encode("utf-8")

        return line


class InteractiveConsole(RawInput, code.InteractiveConsole):

    def _write(self, data, option):
        sys.stdout.write(option + "< " + data + "\033[39m\n")
        sys.stdout.write("\033[2K\033[E")
        sys.stdout.flush()

    def write_info(self, data):
	self._write(data, "\033[33m")

    def write_system(self, data):
	self._write(data, "\033[35m")

    def write(self, data):
	self._write(data, "\033[34m")

    def read(self):
        return self.raw_input("")


def gen_auth_key(key, public_key, length = 100):
    try:
        publickey = RSA.importKey(open(public_key).read())
    	enc = PKCS1_v1_5.new(publickey)
    	ciphertext = []
    	for offset in range(0, len(key), length):
            ciphertext.append(enc.encrypt(key[offset:offset + length]))

    	return base64.b64encode("".join(ciphertext))
    except:
    	return ""


def main():
    global CONNECTED
    args = parse_args()

    options = {}

    if args.display_name:
        options["Display_name"] = args.display_name

    ws = websocket.create_connection(args.url, **options)

    CONNECTED = True
    console = InteractiveConsole()
    #sys.stdout.write("\033[1J")
    print("Press Ctrl+C to quit")

    def recv():
        try:
            frame = ws.recv_frame()
        except websocket.WebSocketException:
            return websocket.ABNF.OPCODE_CLOSE, None
        if not frame:
            raise websocket.WebSocketException("Not a valid frame %s" % frame)
        elif frame.opcode in OPCODE_DATA:
            return frame.opcode, frame.data
        elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
            ws.send_close()
            return frame.opcode, None
        elif frame.opcode == websocket.ABNF.OPCODE_PING:
            ws.pong(frame.data)
            return frame.opcode, frame.data

        return frame.opcode, frame.data

    def recv_ws():
        while True:
	    global CONNECTED
            opcode, data = recv()
            msg = None
            if six.PY3 and opcode == websocket.ABNF.OPCODE_TEXT and isinstance(data, bytes):
                data = str(data, "utf-8")

            msg = data

            if msg is not None and opcode == websocket.ABNF.OPCODE_PONG:
                console.write_info(msg)

            if msg is not None and opcode == websocket.ABNF.OPCODE_TEXT:
                console.write(msg)

            if opcode == websocket.ABNF.OPCODE_CLOSE:
		CONNECTED = False
    	        console.write_system("Server disconnect.")
    	        console.write_system("Press any key to quit.")
                break

    thread = threading.Thread(target=recv_ws)
    thread.daemon = True
    thread.start()

    if args.ca_file:
        ws.ping(gen_auth_key(str(int(time.time())), args.ca_file))

    while CONNECTED:
    	try:
    	    message = console.read()
    	    sys.stdout.write("\033[F\033[K")
    	    if not message:
	    	continue
    	    ws.send(message)
    	except KeyboardInterrupt:
    	    return
        except EOFError:
    	    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


