'''
%
%
%   Blockchain and Future Society
%   GIST
%   Rep. of Korea
%
%   Prof. Heung-No Lee
%   HW for Python Programming of Blockchain
%   Oct. 2018
%   Programmed and Submitted by Jae Hyuck Jang
%
'''

from threading import Thread, Event

import time
from flask import Flask, jsonify, request
import requests
import hashlib
import json
from urllib.parse import urlparse
from uuid import uuid4

import random

from blockchain_core import blockchain
from blockchain_core import app
from blockchain_core import INTERRUPT_EVENT1
from blockchain_core import INTERRUPT_EVENT2
from blockchain_core import STOP_EVENT

blockchain.mining_reward_address='Miner1'

class LoopThread(Thread):
    def __init__(self, stop_event, interrupt_event1, interrupt_event2):
        self.stop_event = stop_event
        self.interrupt_event1 = interrupt_event1
        self.interrupt_event2 = interrupt_event2
        Thread.__init__(self)

    def run(self):
        # Maximum blocks to be mined is set at 20
        while len(blockchain.chain)< blockchain.max_blocks and not self.stop_event.is_set():
            self.loop_process()
            if self.interrupt_event1.is_set():
                self.interrupted_process1()
                self.interrupt_event1.clear()
            if self.interrupt_event2.is_set():
                self.interrupted_process2()
                self.interrupt_event2.clear()
        print("Mining completed")
    def loop_process(self):
        blockchain.mine()
        #print("Mining success!")
        #blockchain.announcement()

    def interrupted_process1(self):
        blockchain.resolve_conflicts()
        blockchain.update_transactions()
        print("Updated")

    def interrupted_process2(self):
        print("asd")


thread = LoopThread(STOP_EVENT, INTERRUPT_EVENT1, INTERRUPT_EVENT2)
@app.route("/mine/auto")
def auto_mine():
    blockchain.resolve_conflicts()
    thread.start()
    return "Mining starts", 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.21', port=2000)