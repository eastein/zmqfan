import pprint
import zmqfan.zmqsub
import sys

if __name__ == '__main__' :
    url = sys.argv[1]
    modes = sys.argv[2:]
    zs = zmqfan.zmqsub.ConnectSub(url)
    while True :
        try :
            msg = zs.recv(timeout=0.05)
            if 'dict_summary' in modes :
                if type(msg) == dict :
                    msg = dict([(k, type(v)) for (k,v) in msg.items()])

            pprint.pprint(msg)
        except zmqfan.zmqsub.NoMessagesException :
            continue
