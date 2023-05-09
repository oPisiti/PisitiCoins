import json
import random
import secrets
import os
from getch import getch
from SHA256 import *
from OptionsMenu import *

class Block():
    def __init__(self, number, prev_hash, from_id, to_id, value, miner):
        self.block = {
            "previous hash": prev_hash,
            "number": number,
            "from": from_id,
            "to": to_id,
            "value": value,
            "miner": miner,
            "miner reward": 10000
        }      
    
    def calculate_hash(self):        
        # Full message
        base_message = det_string(self.block['previous hash'], self.block['number'], self.block['from'], self.block['to'], self.block['value'], self.block['miner'], self.block['miner reward'])
        nonce = 0
        difficulty = 2
        compare = "0" * difficulty

        os.system('cls')

        while True:
            print(f"Trying nonce {nonce}", end = "\r")

            message = base_message + hex(nonce)
            this_hash = SHA256(message)
            
            if this_hash[0:difficulty] != compare:                
                nonce += 1
            else:
                os.system('cls')
                print(f"Block MINED. Adding {self.block['miner reward']} to {self.block['miner']} as miner reward")
                print(f"nonce: {nonce}")
                print(f"Hash: {this_hash}")
                print("")
                break

        self.block['hash'] = "0x" + this_hash
        self.block['nonce'] = nonce

    def chain_block(self, json_file):
        with open(json_file) as block_json:
            read_chain = json.load(block_json)
            read_chain['BlockChain'].append(self.block) 

        with open(json_file, 'w') as outfile:
            json.dump(read_chain, outfile)
                

def AccountBalance(from_id):
    # Returns the account balance for a specific account
    with open('PisitiCoin.json') as block_json:
        read_chain = json.load(block_json)
        balance = 0
        for block in read_chain['BlockChain']:
            if from_id == block['miner']:
                balance += block['miner reward']
            
            if from_id == block['to']:
                balance += block['value']

            if from_id == block['from']:
                balance -= block['value']
    
    return balance


def det_string(previous_hash, number, from_id, to_id, value, miner, miner_reward):
    return previous_hash[2:] + format(number, '#066x')[2:] + from_id[2:] + to_id[2:] + format(value, '#066x')[2:] + miner[2:] + format(miner_reward, '#066x')[2:]


def PisitiCoin(from_id, to_id, value, miner):
    # Checking the number of blocks
    with open('PisitiCoin.json') as block_json:
        read_chain = json.load(block_json)
        size = len(read_chain['BlockChain'])
        prev_hash = read_chain['BlockChain'][size-1]['hash']

    from_balance = AccountBalance(from_id)
    
    if from_balance <= value:
        print(f"Account {from_id} balance: {from_balance} PisitiCoins")
        print(f"Insufficient funds in account {from_id}. Aborting operation")

    else:
        new_block = Block(size, prev_hash, from_id, to_id, value, miner)

        new_block.calculate_hash()
        new_block.chain_block('PisitiCoin.json')


def check_chain_validity(check_last = 10, check_all = False):   
    with open('PisitiCoin.json') as block_json:
        read_chain = json.load(block_json)
        chain = read_chain["BlockChain"]
        size = len(chain)
        start = size - check_last

        if check_all:
            start = 0

        if start < 0:
            start = 0

        valid = True
        for i in range(start, size):
            message = det_string(chain[i]['previous hash'], chain[i]['number'], chain[i]['from'], chain[i]['to'], chain[i]['value'], chain[i]['miner'], chain[i]['miner reward'])   
            message += hex(chain[i]['nonce'])  

            this_hash = "0x" + SHA256(message)

            if this_hash != chain[i]['hash']:
                print(f"Inconsistency located in block {i}")
                print(f"Hash: {this_hash}")
                valid = False
                break
            
        if valid:
            print(f"All blocks are valid!")
            print("")


if __name__ == "__main__":

    file_name = 'PisitiCoin.json'

    # Interface
    while True:
        print("-------------------------------------")
        print("| Welcome to PisitiCoin's Interface |")
        print("-------------------------------------")
        print("")
        greeting = "What do you wish to do?"
        options = ["See Account Balance", "Send PisitiCoins", "Check Block Chain Validity", "Show Latest blocks", "Quit"]
        answer = OptionsMenu(options, greeting)
        os.system('cls')

        with open(file_name) as block_json: 
            read_data = json.load(block_json)
            pkeys = read_data['Public keys']

        if answer == "See Account Balance":
            greeting = "Choose and account"        
            answer = OptionsMenu(pkeys, greeting)
            
            acc_balance = AccountBalance(answer)
            os.system('cls')
            print(f"Account {answer} has {acc_balance} PisitiCoins")
            input()
        
        elif answer == "Send PisitiCoins":
            while True:
                greeting = "Choose your account"        
                from_id = OptionsMenu(pkeys, greeting)
                os.system('cls')

                greeting = "Choose the account you wish to transfer to"        
                to_id = OptionsMenu(pkeys, greeting)
                os.system('cls')
                
                amount = int(input("How many PisitiCoins to transfer? "))

                if amount < 0:
                    amount *= -1

                greeting = f"You wish to transfer {amount} PisitiCoins from {from_id} to {to_id}, correct?"
                options = ["Yes", "No"]
                if OptionsMenu(options, greeting) == "Yes":
                    break
            
            miner = secrets.choice(read_data['Public keys'])
            PisitiCoin(from_id, to_id, amount, miner)
            input()

        elif answer == "Show Latest blocks":
            amount = int(input("How many blocks do you wish to see? "))
            os.system('cls')
            
            with open(file_name) as block_json: 
                read_data = json.load(block_json)    
                blockChain_len = len(read_data['BlockChain'])

                if amount > blockChain_len:
                    amount = blockChain_len

                blocks = read_data['BlockChain'][blockChain_len - amount:]

                for block in blocks:
                    print(f"Block Number {block['number']}")                  
                    print(f"Previous Hash: {block['previous hash']}")
                    print(f"From {block['from']}")
                    print(f"To {block['to']}")
                    print(f"Amount: {block['value']} PisitiCoins")
                    print(f"Mined By {block['miner']}")
                    print(f"Miner Reward: {block['miner reward']} PisitiCoins")
                    print(f"Nonce: {block['nonce']}")
                    print(f"Hash: {block['hash']}", end = "\r\n\n")

            input()


        elif answer == "Check Block Chain Validity":
            check_chain_validity(check_all = True)
            input()

        elif answer == "Quit":
            break

        os.system('cls')