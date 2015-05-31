from zmqfan import zmqsub
import unittest

class SelectionTests(unittest.TestCase):
    def test_mkindex_integers(self):
        idx, alist = zmqsub._mkindex([2])
        self.assertEquals([2], alist)
        self.assertEquals({}, idx)
        self.assertEquals([2], zmqsub._useindex([2], {}))
