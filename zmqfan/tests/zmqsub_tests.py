from zmqfan import zmqsub
import zmq.core.error
import unittest
import random
import time
import threading

IP = '127.0.0.1'
URLPAT = 'tcp://%s:%s' % (IP, '%d')

def tcp_port_chooser(cls, *a, **kw) :
	LOW = 2000
	HIGH = 65535
	TRIES = 100

	ze = None
	t = 0
	while t < TRIES :
		try :
			port = random.randint(LOW, HIGH)
			url = URLPAT % port
			return url, cls(url, *a, **kw)
		except zmq.core.error.ZMQError, _ze :
			ze = _ze
		t += 1

	raise ze



class Inproc(object) :
	X = 0
	INPROCURLPAT = 'inproc://url%d'

	@classmethod
	def pick(cls) :
		cls.X += 1
		return cls.INPROCURLPAT % cls.X

def inproc_chooser(cls, *a, **kw) :
	url = Inproc.pick()
	return url, cls(url, *a, **kw)

# tcp port chooser requires some time to wait for the connection to open up.
#cchooser = tcp_port_chooser
cchooser = inproc_chooser

class BasicTests(unittest.TestCase) :
	def test_1_msg_bindpub(self) :
		url, pub = cchooser(zmqsub.BindPub)
		sub = zmqsub.ConnectSub(url, context=pub)
		pub.send({'a' : 'b'})
		self.assertEquals({'a': 'b'}, sub.recv(timeout=5.0))

	def test_1_msg_connectpub(self) :
		url, sub = cchooser(zmqsub.BindSub)
		pub = zmqsub.ConnectPub(url, context=sub)
		pub.send({'a' : 'b'})
		self.assertEquals({'a': 'b'}, sub.recv(timeout=5.0))


