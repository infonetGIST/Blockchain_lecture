''' 

  

   Python Programming of Blockchain   

  

   was a series of three lectures given within the Graduate Course 

   'Blockchain and Future Society' 

   Offered in the Fall Semester 2018 at 

   GIST, Rep. of Korea. The instructor was Prof. Heung-No Lee. 

   The blockchain developed in the course was not meant to be complete. 

   Instead, aim was to understand 

   what a blockchain, and a cryptocurrency based on it, is by 

   doing a little bit of programming work. 

   

   To this end, Prof. Lee utilized the blog work 

   "Learn Blockchain by Building One" of Daniel Flymen [1],[2]. 

   Flymen's blog and his Python code offerred good introductory materials. 

   His code was also given to learn blockchain and thus was not meant to be complete. 

    

   In my course, I have given a homework assignment to improve on his work. 

   The code presented below was a result of homework assignment which 

   a group of students have worked together and made improvements. 

  

   There were several upgrades made to [2]. Just to name a few notable ones, they are 

   1) mined blocks now have "correct" block hashes with the designated leading 

   number of zeros. 2) A auto mining routine was included in which 

   the mining operation is continued at a node which listens 

   to a new block announcement and switches if a new longest chain is found. 

    

   Overall the list of functions this code can demonstrate includes: 

    1. Announcing transactions, 

    2. Including transactions into blocks, 

    3. Chaining blocks using Proof-of-Work(PoW), 

    4. Chainging the level of PoW difficulty 

        by varying the number of leading zeros in hash values, 

    5. Following the consensus rule of the longest-chain-win, and 

    6. Interworking of peer-to-peer nodes using APIs. 

   

  The source code and the relevant lecture note are available to download here in [3],[4]. 

   

    

References      :   [1] Daniel van Flymen, "Learn Blockchain by Building One," 

                        Sept. 25th, 2017, https://hackernoon.com/learn-blockchains-by-building-one-117428612f46.  

                    [2] Daniel van Flymen, Source code at https://github.com/dvf/blockchain/blob/master/blockchain.py. 

                    [3] Heung-No Lee, "Lecture Note on Python Programming of Blockchain," https://infonet.gist.ac.kr. 

                    [4] Heung-No Lee, Source Code of Python Programming of Blockchain," https://github.com/infonetGIST/Blockchain_lecture. 

  
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

STOP_EVENT = Event()
INTERRUPT_EVENT1 = Event()
INTERRUPT_EVENT2 = Event()

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.awaiting_transactions =[]
        self.chain = []
        self.nodes = set()
        self.published_transactions_ID = []
        self.mining_reward_address='0'
        self.MY_NODE_ADDRESS='0'
        # Generate a globally unique address for this node
        self.node_identifier = str(uuid4()).replace('-', '')
        # node_identifier = hex(random.randrange(1, 9999999))
        self.interrupt_flag=False
        self.max_blocks = 30

        dummy_block = {
            'index': 0,
            'timestamp': 0,
            'transactions': [],
            'proof': 0,
            'previous_hash': 0,
        }
        Ini_proof = self.proof_of_work(mining_time=0, last_block=dummy_block)
        self.new_block(previous_hash='0', mining_time=0, proof=Ini_proof)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            prev_block=chain[current_index-1]
            #print(f'{last_block}')
            #print(f'{block}')
            #print("\n-----------\n")
            # Check that the hash of the block is correct
            prev_block_hash = self.hash(prev_block)
            if block['previous_hash'] != prev_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(block):
                return False

            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
                    best_node = node

        # Replace our chain if we discovered a new, valid chain longer than ours
            if new_chain is not None:
                self.chain = new_chain
                self.make_published_TXID_list()
                #response2 = requests.get(f'http://{best_node}/get_transactions')
                #self.current_transactions = response2.json()['transactions']
                print("Chain replaced")
                return True

        return False

    def new_block(self, mining_time, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': mining_time,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        self.make_published_TXID_list()
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        TX_time=time.time()
        transaction_dummy = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'transaction time': TX_time
        }
        TXID = self.hash(transaction_dummy)
        new_TX_content = {
            'TXID': TXID,
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'transaction time': TX_time
        }
        if self.is_valid_TX(new_TX_content):
            self.current_transactions.append(new_TX_content)
            self.node_identifier = str(uuid4()).replace('-', '')
            return self.last_block['index'] + 1
        else:
            return None

    def update_transactions(self):

        #neighbours = self.nodes

        my_transactions = self.current_transactions
        my_TX_length = len(self.current_transactions)
        flag = 2
        #for node in neighbours:
        her_response = requests.get(f'http://127.0.0.24:2000/get_awaiting_transactions')
        if her_response.status_code == 200 and her_response.json()['length']:
            her_TX_length = her_response.json()['length']
            her_awaiting_transactions = her_response.json()['awaiting_transactions']
            for j in range(her_TX_length):
                her_TXID = her_awaiting_transactions[j]['TXID']
                flag = 1
                for i in range(my_TX_length):
                    my_TXID = my_transactions[i]['TXID']
                    if my_TXID == her_TXID:
                        flag = 0
                if flag == 1 and self.is_valid_TX(her_awaiting_transactions[j]):
                    self.current_transactions.append(her_awaiting_transactions[j])
        return flag

    def is_valid_TX(self, transaction):
        flag = 1
        for i in range(len(self.published_transactions_ID)):
            if self.published_transactions_ID[i] == transaction['TXID']:
                flag = 0
        if flag == 1:
            return True
        else:
            return False

    def check_current_TXs_validity(self):
        flag = 1
        k = 1
        TX_length = len(self.current_transactions)
        while k <= TX_length:
            if self.is_valid_TX(self.current_transactions[k]):
                k += 1
            else:
                del self.current_transactions[k]
                TX_length -= 1
                flag = 0
        if flag == 1:
            return True
        else:
            return False

    def update_awaiting_TX(self):
        latest_published_TXID = self.published_transactions_ID
        length_LPTXID = len(latest_published_TXID)
        awaiting_transactions = self.awaiting_transactions
        length_ATX = len(awaiting_transactions)
        updated_awaiting_transactions = []

        for i in range(length_ATX):
            flag = 1
            for j in range(length_LPTXID):
                if awaiting_transactions[i]['TXID'] == latest_published_TXID[j]:
                    flag = 0
            if flag == 1:
                updated_awaiting_transactions.append(awaiting_transactions[i])
        self.awaiting_transactions = updated_awaiting_transactions
        return self.awaiting_transactions

    def make_published_TXID_list(self):
        self.published_transactions_ID = []
        chain_length = len(self.chain)
        for i in range(chain_length):
            i_published_transactions = self.chain[i]['transactions']
            i_TX_length = len(i_published_transactions)
            for j in range(i_TX_length):
                i_j_TXID = i_published_transactions[j]['TXID']
                self.published_transactions_ID.append(i_j_TXID)
        return self.published_transactions_ID

    def announcement(self):
        neighbours = self.nodes
        for node in neighbours:
            response = requests.get(f'http://{node}/get_updates')
    def mine(self):
        # We run the proof of work algorithm to get the next proof...
        last_block = self.last_block
        mining_time = time.time(),
        randomSTR = str(uuid4()).replace('-', '')
        self.new_transaction(
            sender="Coinbase transaction",
            recipient=self.mining_reward_address + '  #' + randomSTR,
            amount=1,
        )
        proof = self.proof_of_work(mining_time, last_block)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.

        # Forge the new Block by adding it to the chain
        if proof==0:
            del self.current_transactions[-1]
        else:
            previous_hash = self.hash(last_block)
            block = self.new_block(mining_time, proof, previous_hash)
            print("Mining success!")
            self.announcement()


    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, mining_time, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        if len(self.chain) == 0:
            last_hash = '0'
        else:
            last_hash = self.hash(last_block)

        proof = 0
        test_block = {
            'index': len(self.chain) + 1,
            'timestamp': mining_time,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': last_hash or self.hash(self.chain[-1]),
        }
        while self.valid_proof(test_block) is False:
            if self.interrupt_flag:
                blockchain.interrupt_flag = False
                return 0

            proof += 1
            test_block = {
                'index': len(self.chain) + 1,
                'timestamp': mining_time,
                'transactions': self.current_transactions,
                'proof': proof,
                'previous_hash': last_hash or self.hash(self.chain[-1]),
            }

        return proof

    @staticmethod
    def valid_proof(test_block):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """
        block_string = json.dumps(test_block, sort_keys=True).encode()
        guess_hash = hashlib.sha256(block_string).hexdigest()
        # guess = f'{last_proof}{proof}{last_hash}'.encode()
        # guess_hash = hashlib.sha256(guess).hexdigest()
        # Difficulty Level is adjusted here!  The number of leading zeros shall be
        # changed together with the :4 number in the parenthesis. 
        return guess_hash[:5] == "00000"

# Instantiate the Blockchain
blockchain = Blockchain()

# Instantiate the Node
app = Flask(__name__)

@app.route('/mine', methods=['GET'])
def mine():
    blockchain.mine()
    block=blockchain.last_block
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    # INTERRUPT_EVENT1.set()
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/get_transactions', methods=['GET'])
def full_transactions():
    # INTERRUPT_EVENT2.set()
    response = {
        'transactions': blockchain.current_transactions,
        'length': len(blockchain.current_transactions),
    }
    return jsonify(response), 200

@app.route('/get_awaiting_transactions')
def awaiting_transactions():
    response = {
        'awaiting_transactions': blockchain.awaiting_transactions,
        'length': len(blockchain.awaiting_transactions),
    }
    return jsonify(response), 200

@app.route('/get_updates')
def receiving_longest_chain_and_update_TX_list():
    INTERRUPT_EVENT1.set()
    blockchain.interrupt_flag=True
    return "ask received", 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

# http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/shutdown")
def shutdown():
    STOP_EVENT.set()
    thread.join()
    shutdown_server()
    return "OK", 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=2000)
