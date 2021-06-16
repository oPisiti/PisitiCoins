import json
import random
import secrets
import os
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
        # print(format(self.number, '#066x'))
        
        # Full message
        # base_message = self.block['previous hash'][2:] + format(self.block['number'], '#066x')[2:] + self.block['from'][2:] + self.block['to'][2:] + format(self.block['value'], '#066x')[2:] + self.block['miner'][2:] + format(self.block['miner reward'], '#066x')[2:]
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

        # print(this_hash)

        self.block['hash'] = "0x" + this_hash
        self.block['nonce'] = nonce
        # print(self.block)

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
    # print(f"OIOIOI: {format(miner_reward, '#066x')[2:]}")
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
            # print(f"previous hash: {chain[i]['previous hash']}")
            # print(f"number: {chain[i]['number']}")
            # print(f"from: {chain[i]['from']}")
            # print(f"to: {chain[i]['to']}")
            # print(f"value: {chain[i]['value']}")
            # print(f"miner: {chain[i]['miner']}")
            # print(f"miner reward: {chain[i]['miner reward']}")

            message = det_string(chain[i]['previous hash'], chain[i]['number'], chain[i]['from'], chain[i]['to'], chain[i]['value'], chain[i]['miner'], chain[i]['miner reward'])   
            message += hex(chain[i]['nonce'])  
            # print(f"nonce: {hex(chain[i]['nonce'])}")
            # print(f"Message: {message}")

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
    # Interface
    while True:
        print("-------------------------------------")
        print("| Welcome to PisitiCoin's Interface |")
        print("-------------------------------------")
        print("")
        greeting = "What do you wish to do?"
        options = ["See Account Balance", "Send PisitiCoins", "Check Block Chain Validity", "Quit"]
        answer = OptionsMenu(options, greeting)
        os.system('cls')

        with open('PisitiCoin.json') as block_json: 
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

        elif answer == "Check Block Chain Validity":
            check_chain_validity(check_all = True)

            input()

        elif answer == "Quit":
            break

        os.system('cls')



    ## For adding random transactions
    # with open('PisitiCoin.json') as block_json: 
    #     read_data = json.load(block_json)
    #     miner = secrets.choice(read_data['Public keys'])
    #     # from_id = secrets.choice(read_data['Public keys'])
    #     from_id = "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf"

    #     while True:
    #         to_id = secrets.choice(read_data['Public keys'])
    #         if to_id != from_id:
    #             break  

    # value = int(random.random()*100)

    # PisitiCoin(from_id, to_id, value, miner)



    ## For adding the first block - Requires changes in function PisitiCoin
    ## like fixing size and previous hash
    # miner = "0x69240a05f2e6a5fc533a5861abfb94d8af8e9fc9"
    # from_id = "0x0000000000000000000000000000000000000000"
    # to_id = "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf"
    # value = 73611

    # PisitiCoin(from_id, to_id, value, miner)