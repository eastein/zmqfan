import codecs
import zmq
import json

class NoMessagesException(Exception):
    pass


def debugp(s):
    import time
    print('%0.4f: %s' % (time.time(), s))

def _mkindex(sockets):
    """
    Make an index from sockets.
    :param sockets: list of sockets; Each socket may be of type JSONZMQ or type socket.socket
    :return: need to work that out.. sorry. I should have documented this when I wrote it.
    """
    items_remaining = len(sockets)
    idx = dict(map(lambda s: (s.fileno(), s), filter(lambda s: hasattr(s, 'fileno'), sockets)))
    debugp("was able to put %d items in the index using file numbers" % len(idx))
    nl = list(idx.values())
    items_remaining -= len(nl)
    debugp("building remainder of index, %d items to go" % items_remaining)
    for s in sockets:
        debugp("figuring out where to put %s in the index" % s)
        if isinstance(s, JSONZMQ):
            debugp("%s is a JSONZMQ, inserting its core socket %s in idx" %(s,  s.s))
            idx[s.s.fd] = s
            nl.append(s.s.fd)
            items_remaining -= 1
        elif isinstance(s, int):
            debugp("%s is a raw FD, no need to index")
            items_remaining -= 1
            nl.append(s)
        elif isinstance(s, zmq.Socket):
            debugp("%s is a zmq socket, indexing by fd")
            idx[s.fd] = s
            nl.append(s.fd)

    debugp("at index build end %d items were not usable" % items_remaining)

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
        debugp('%s is in activelist' % s)
        if s in index:
            r.append(index[s])
        else:
            r.append(s)
    return r


def select(rlist, wlist, xlist, timeout):
    rindex, rlist = _mkindex(rlist)
    windex, wlist = _mkindex(wlist)
    xindex, xlist = _mkindex(xlist)

    r, w, x = zmq.select(rlist, wlist, xlist, timeout)

    return _useindex(r, rindex),  _useindex(w, windex), _useindex(x, xindex)


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
            self._last = json.loads(codecs.decode(msg, 'utf8'))

        return self._last

    def recv(self, timeout=0.0):
        msg = None
        r, w, x = zmq.select([self.s], [], [], timeout)
        if r:
            msg = codecs.decode(self.s.recv(), 'utf8')
            self._last = json.loads(msg)
            return self._last
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
        msg = None
        r, w, x = zmq.select([self.s], [], [], timeout)
        if r:
            msg = self.s.recv()
            try:
                self._last = json.loads(msg)
                return self._last
            except ValueError:
                pass
        else:
            raise NoMessagesException
