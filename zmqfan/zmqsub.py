from __future__ import absolute_import
from __future__ import print_function
import codecs
import zmq
import json
import time


class NoMessagesException(Exception):
    pass

VERBOSE = False


def debugp(s):
    print(('%0.4f: %s' % (time.time(), s)))


def _mkindex(sockets):
    idx = dict([(s.fileno(), s) for s in [s for s in sockets if hasattr(s, 'fileno')]])
    nl = []
    for s in sockets:
        if isinstance(s, JSONZMQ):
            idx[s.s] = s
            nl.append(s.s)
        else:
            nl.append(s)

    return idx, nl


def _useindex(activelist, index):
    """
    Given a list of items returned from zmq.select and the index made by _mkindex, return the list of objects
       that were originally given to _mkindex - those that are active.
    :param activelist:
    :param index:
    :return:
    """
    r = []
    for s in activelist:
        if VERBOSE:
            debugp('%s is in activelist' % s)
        if s in index:
            if VERBOSE:
                debugp("%s was ind index. found item %s" % (s, index[s]))
            r.append(index[s])
        else:
            if VERBOSE:
                debugp("%s was not in index, so passed it through without checking it.")
            r.append(s)
    return r


def decode_utf8_json(buf):
    try:
        unicode_msg = codecs.decode(buf, 'utf-8')
        return json.loads(unicode_msg)
    except UnicodeDecodeError:
        raise ValueError("message was not valid utf-8.")


def select(rlist, wlist, xlist, timeout):
    i, rlist = _mkindex(rlist)
    wi, wlist = _mkindex(wlist)
    xi, xlist = _mkindex(xlist)

    i.update(wi)
    i.update(xi)

    r, w, x = zmq.select(rlist, wlist, xlist, timeout)

    return _useindex(r, i),  _useindex(w, i), _useindex(x, i)


class JSONZMQ(object):

    def get_context(self, context):
        """
        If given a context, return it.
        If given a JSONZMQ, extract the context from that.
        If given no context, create one.
        """
        if context is None:
            return zmq.Context(1)
        elif isinstance(context, JSONZMQ):
            return context.c
        else:
            return context


class ConnectSub(JSONZMQ):

    def __init__(self, url, context=None):
        self.c = self.get_context(context)
        self.s = self.c.socket(zmq.SUB)
        self.s.setsockopt(zmq.SUBSCRIBE, b"")
        self.s.connect(url)
        self._last = None

    def last_msg(self):
        r = [self.s]
        msg = None
        while r:
            r, w, x = zmq.select([self.s], [], [], 0.0)
            if r:
                msg = self.s.recv()

        r, w, x = zmq.select([self.s], [], [], 0.05)
        if r:
            msg = self.s.recv()

        if msg is not None:
            self._last = decode_utf8_json(msg)

        return self._last

    def recv(self, timeout=0.0):
        msg = None
        r, w, x = zmq.select([self.s], [], [], timeout)
        if r:
            try:
                self._last = decode_utf8_json(self.s.recv())
                return self._last
            except ValueError:
                raise NoMessagesException
        else:
            raise NoMessagesException


class ConnectPub(JSONZMQ):

    def __init__(self, url, context=None):
        self.c = self.get_context(context)
        self.s = self.c.socket(zmq.PUB)
        self.s.connect(url)

    # unreliable send, but won't block forever.
    def send(self, msg, timeout=10.0):
        r, w, x = zmq.select([], [self.s], [], timeout)
        if w:
            self.s.send(codecs.encode(json.dumps(msg), 'utf8'))


class BindPub(JSONZMQ):

    def __init__(self, url, context=None):
        self.c = self.get_context(context)
        self.s = self.c.socket(zmq.PUB)
        self.s.bind(url)

    def send(self, msg):
        self.s.send(codecs.encode(json.dumps(msg), 'utf8'))


class BindSub(JSONZMQ):

    def __init__(self, url, context=None):
        self.c = self.get_context(context)
        self.s = self.c.socket(zmq.SUB)
        self.s.setsockopt(zmq.SUBSCRIBE, b"")
        self.s.bind(url)

    def recv(self, timeout=0.0):
        r, w, x = zmq.select([self.s], [], [], timeout)
        if r:
            try:
                self._last = decode_utf8_json(self.s.recv())
                return self._last
            except ValueError:
                raise NoMessagesException
        else:
            raise NoMessagesException
