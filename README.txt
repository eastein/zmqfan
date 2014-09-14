# Helper Code for ZMQ Usage

Primary purpose is shuffling around JSON.

## zmqsub

This module is for decoding & encoding JSON and receiving & sending it over sockets.

*It's a little bit dodgy at the moment, needs some shine & polish.*  Particularly, it needs better error handling and a more flexible API. Not yet 1.0, so the API could change. If you need stability, use a git commit id or an exact version number in PyPI.

### zmqsub unit tests

    cd zmqfan
    nosetests -vv tests/
