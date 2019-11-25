#!/usr/bin/env python2.7
import unittest
import sys, os

from threading import Thread
from websocket_server import WebsocketServer
from websocket_server import WebSocketHandler

class Calculator:

    def hash_calculations_for_response(self, key):
	return WebSocketHandler.calculate_response_key(key)

    def response_messages(self, key):
	return WebSocketHandler.make_handshake_response(key)


class CalculatorTest(unittest.TestCase):
 
    def test_hash_calculations_for_response(self):
	cal = Calculator()
	self.assertEqual(cal.hash_calculations_for_response('zyjFH2rQwrTtNFk5lwEMQg=='), '2hnZADGmT/V1/w1GJYBtttUKASY=')
	
    def test_response_messages(self):
	expected = \
                'HTTP/1.1 101 Switching Protocols\r\n'\
                'Upgrade: websocket\r\n'              \
                'Connection: Upgrade\r\n'             \
                'Sec-WebSocket-Accept: 2hnZADGmT/V1/w1GJYBtttUKASY=\r\n'\
                '\r\n'

	cal = Calculator()
	self.assertEqual(cal.response_messages('zyjFH2rQwrTtNFk5lwEMQg=='), expected)


if __name__ == '__main__':
    unittest.main()

