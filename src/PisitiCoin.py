import json
import os
import random
import secrets

from helper import *
from OptionsMenu import *


# Change parameters into dictionary
def create_new_block(db: BlockChain, from_id: str, to_id: str, amount: float, miner: str, print_steps = False) -> Block:
    """ Creates and chains a new block if possible """

    from_balance = db.get_account_balance(from_id)
    
    if from_balance <= amount:
        if not print_steps: return 

        print(f"Account {from_id}'s balance: {from_balance} PisitiCoins")
        print(f"Insufficient funds in account {from_id}. Aborting operation")

    # Able to create a block
    else:
        block_info = {
            "from_id":  from_id,
            "to_id":    to_id,
            "amount":   amount,
            "miner_id": miner,
        }

        new_block = Block(db, block_info)

        new_block.mine_block(print_steps = print_steps)
        new_block.chain_block(db)

def run_interface(db_path: str) -> None:
    """ Runs the main interface"""

    greeting = "\n" + \
    "       ___________________________________\n" + \
    "      | Welcome to PisitiCoin's Interface |\n" + \
    "      " + " \u0305"* 35 + \
    "\n\n" + \
    "What do you wish to do?\n"
    

    options = ["See Account Balance", "Send PisitiCoins", "Check Block Chain Validity", "Show Latest blocks", "Quit"]
    
    # Determining the clear screen command based on the OS
    clear_command = "cls" if os.name == "nt" else "clear" 
    os.system(clear_command)

    # Creating a connection to the database
    db = BlockChain(db_path)
    accounts = db.get_accounts_ids_and_usernames()
    accounts_ids = tuple(accounts.keys())

    answer = OptionsMenu(options, greeting)

    if answer == "See Account Balance":
        greeting = "Choose and account"        
        answer = OptionsMenu(accounts_ids, greeting)
        
        acc_balance = db.get_account_balance(answer)
        os.system(clear_command)
        print(f"Account {accounts[answer]} ({answer}) has {acc_balance} PisitiCoins")
    
    elif answer == "Send PisitiCoins":
        while True:
            greeting = "Choose your account"        
            from_id = OptionsMenu(accounts_ids, greeting)
            os.system(clear_command)

            greeting = "Choose the account you wish to transfer to"        
            to_id = OptionsMenu(accounts_ids, greeting)
            os.system(clear_command)
            
            # Getting amount            
            while True:
                try:                    
                    amount = int(input("How many PisitiCoins to transfer? "))
                    break
                except ValueError as e: 
                    continue
                finally:                
                    os.system(clear_command)

            if amount < 0:
                amount *= -1

            greeting = f"You wish to transfer {amount} PisitiCoins from {from_id} to {to_id}, correct?"
            options = ["Yes", "No"]
            if OptionsMenu(options, greeting) == "Yes":
                break
        
        # Getting random miner
        miner = secrets.choice(tuple(db.get_accounts_ids_and_usernames().keys()))
        create_new_block(db, from_id, to_id, amount, miner, print_steps = True)

    elif answer == "Check Block Chain Validity":
        while True:
            amount_blocks = input("How many blocks do you wish to verify? ('a' for all) ")
            
            # If all
            if amount_blocks.lower() == "a": 
                amount_blocks = -1
            
            try:
                # If number
                amount_blocks = int(amount_blocks)
                break

            except ValueError as e:
                pass

        os.system(clear_command)

        error_on_block_id = db.check_chain_validity(amount_blocks)

        if error_on_block_id is None: print("Blockchain is healthy")
        else:                         print(f"Block with id {error_on_block_id} is broken")


    elif answer == "Show Latest blocks":
        while True:
            try:
                amount_blocks = int(input("How many blocks do you wish to see? "))
                break
            except ValueError as e:
                pass

        os.system(clear_command)

        count = 1
        for block in db.get_all_blocks(id_order_asc=False):
            print(f"Block Number {block['id']}")                  
            print(f"Previous Hash: {block['previous_hash']}")
            print(f"From {block['from_id']}")
            print(f"To {block['to_id']}")
            print(f"Amount: {block['amount']} PisitiCoins")
            print(f"Mined By {block['miner_id']}")
            print(f"Miner Reward: {block['miner_reward']} PisitiCoins")
            print(f"Nonce: {block['nonce']}")
            print(f"Hash: {block['hash']}", end = "\r\n\n")

            if count >= amount_blocks: break
            count += 1


    elif answer == "Quit": raise StopIteration()

    input()
    input()
    os.system(clear_command)


if __name__ == "__main__":
    # Changing the current directory in order to use a relative path to the database
    os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    file_name = 'db/PisitiCoin.sqlite3'

    # Interface
    while True:
        try:
            run_interface(file_name)
        except StopIteration as e:
            break