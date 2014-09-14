import zmq
from zmq import Context
import json

class NoMessagesException(Exception) :
	pass

class JSONZMQ(object) :
	def get_context(self, context) :
		"""
		If given a context, return it.
		If given a JSONZMQ, extract the context from that.
		If given no context, create one.
		"""
		if context is None :
			return Context(1)
		elif isinstance(context, JSONZMQ) :
			return context.c
		else :
			return context

class ConnectSub(JSONZMQ) :
	def __init__(self, url, context=None) :
		self.c = self.get_context(context)
		self.s = self.c.socket(zmq.SUB)
		self.s.setsockopt (zmq.SUBSCRIBE, "")
		self.s.connect(url)
		self._last = None

	def last_msg(self) :
		r = [self.s]
		msg = None
		while r :
			r, w, x = zmq.select([self.s], [], [], 0.0)
			if r :
				msg = self.s.recv()

		r, w, x = zmq.select([self.s], [], [], 0.05)
		if r :
			msg = self.s.recv()

		if msg is not None :
			self._last = json.loads(msg)

		return self._last

	def recv(self, timeout=0.0) :
		msg = None
		r, w, x = zmq.select([self.s], [], [], timeout)
		if r :
			msg = self.s.recv()
			self._last = json.loads(msg)
			return self._last
		else :
			raise NoMessagesException

class ConnectPub(JSONZMQ) :
	def __init__(self, url, context=None) :
		self.c = self.get_context(context)
		self.s = self.c.socket(zmq.PUB)
		self.s.connect(url)

	# unreliable send, but won't block forever.
	def send(self, msg) :
		r, w, x = zmq.select([], [self.s], [], 10.0)
		if w :
			self.s.send(json.dumps(msg))
		
class BindPub(JSONZMQ) :
	def __init__(self, url, context=None) :
		self.c = self.get_context(context)
		self.s = self.c.socket(zmq.PUB)
		self.s.bind(url)

	def send(self, msg) :
		self.s.send(json.dumps(msg))

class BindSub(JSONZMQ) :
	def __init__(self, url, context=None) :
		self.c = self.get_context(context)
		self.s = self.c.socket(zmq.SUB)
		self.s.setsockopt (zmq.SUBSCRIBE, "")
		self.s.bind(url)


	def recv(self, timeout=0.0) :
		msg = None
		r, w, x = zmq.select([self.s], [], [], timeout)
		if r :
			msg = self.s.recv()
			try :
				self._last = json.loads(msg)
				return self._last
			except ValueError :
				pass
		else :
			raise NoMessagesException
