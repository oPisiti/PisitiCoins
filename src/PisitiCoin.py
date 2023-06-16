import os
import random
import re
import secrets

from passlib.hash import pbkdf2_sha256

from helper import *
from OptionsMenu import *


class Globals:
    """
    Global variables
    """

    CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
    LOGGED_IN_AS = "None"


class Colors:
    """
    Nice colors :)
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    UPONELINE = '\033[F'


def create_and_chain_block(db: BlockChain, block_data: dict) -> Block:
    """ 
    Creates and chains a new block if possible 
    block_data must have as keys:
        - "from_id":  str
        - "to_id":    str
        - "amount":   float
        - "miner_id": str

    Raises ValueError if account from_id does not have enough cash for the transaction
    """

    # Checking block_data keys
    required_keys = ("from_id", "to_id", "amount", "miner_id")
    if tuple(block_data.keys()) != required_keys:
        raise KeyError(
                f"""
                Keys from provided dictionary are incorrect
                Required keys: {required_keys}
                """
                )

    from_balance = db.get_account_balance(block_data["from_id"])
    amount = block_data["amount"]
    
    # Checking if enough cash
    if from_balance <= amount:
        raise ValueError(
            f"""
            Insufficient funds on account {block_data["from_id"]}.
            Available cash: {from_balance}.
            Required cash:  {amount}.
            """
        ) 

    # Able to create a block
    else:
        new_block = Block(db, block_data)

        new_block.mine_block(print_steps = os.environ["PRINT_STEPS"] == "True")
        new_block.chain_block(db)


def get_interface_greeting() -> str:
    """
    Returns updated greeting message
    """

    return "\n" + \
    "                          _____  _       _  _    _   _____        _        \n" + \
    "                         |  __ \(_)     (_)| |  (_) / ____|      (_)       \n" + \
    "                         | |__) |_  ___  _ | |_  _ | |      ___   _  _ __  \n" + \
    "                         |  ___/| |/ __|| || __|| || |     / _ \ | || '_ \ \n" + \
    "                         | |    | |\__ \| || |_ | || |____| (_) || || | | |\n" + \
    "                         |_|    |_||___/|_| \__||_| \_____|\___/ |_||_| |_|\n" + \
    "\n\n" + \
    (f"{Colors.OKCYAN}Logged in as {Colors.BOLD}{Globals.LOGGED_IN_AS}{Colors.ENDC}\n" if Globals.LOGGED_IN_AS is not None else \
     f"{Colors.FAIL}Not logged in{Colors.ENDC}\n")


def get_interface_options() -> tuple:
    """
    Returns updated options
    """

    not_logged_in = (
        "Log In",
        "Sign Up",
        "See Accounts Balances",
        "Update All balances",
        "Check Block Chain Validity",
        "Fix Block Chain",
        "Remine All Blocks",
        "Show Latest blocks",
        "Quit"
    )

    logged_in = (
        "See Accounts Balances",
        "Send PisitiCoins",
        "Update All balances",
        "Check Block Chain Validity",
        "Fix Block Chain",
        "Remine All Blocks",
        "Show Latest blocks",
        "Log Out",
        "Quit"
    )

    if Globals.LOGGED_IN_AS is None: return not_logged_in
    else:                            return logged_in


def show_latest_blocks(db: BlockChain) -> None:
    while True:
        amount_blocks = input("How many blocks do you wish to see? ('a' for all) ")
        
        # If all
        if amount_blocks.lower() == "a": 
            amount_blocks = len(db.get_blocks_ids())

        try:
            amount_blocks = int(amount_blocks)
            break
        except ValueError as e:
            pass

    os.system(Globals.CLEAR_COMMAND)

    count = 1
    for block in db.get_all_blocks(id_order_asc=False):
        print(f"Block {Colors.BOLD}#{block['id']}{Colors.ENDC}")                  
        print(f"Previous Hash: {block['previous_hash']}")
        print(f"From:          {block['from_id']}")
        print(f"To:            {block['to_id']}")
        print(f"Amount:        P$ {block['amount']}")
        print(f"Mined By:      {block['miner_id']}")
        print(f"Miner Reward:  P$ {block['miner_reward']}")
        print(f"Nonce:         {block['nonce']}")
        print(f"Hash:          {block['hash']}", end = "\r\n\n")

        if count >= amount_blocks: break
        count += 1


def run_interface(db_path: str) -> None:
    """ Runs the main interface"""

    greeting = get_interface_greeting()
    
    # Constants
    os.environ["PRINT_STEPS"] = "True"

    options = get_interface_options()
    
    os.system(Globals.CLEAR_COMMAND)

    # Creating a connection to the database
    db = BlockChain(db_path)
    accounts = db.get_accounts_ids_and_usernames()
    accounts_ids = tuple(f"{username} ({_id})" for _id, username in accounts.items())

    answer = OptionsMenu(options, greeting)

    match answer:
        case "Check Block Chain Validity":
            while True:
                amount_blocks = input("How many blocks do you wish to verify? ('a' for all) ")
                
                # If all
                if amount_blocks.lower() == "a": 
                    amount_blocks = -1
                
                try:
                    amount_blocks = int(amount_blocks)
                    break
                except ValueError as e:
                    pass

            os.system(Globals.CLEAR_COMMAND)

            error_on_block_id = db.check_chain_validity(amount_blocks)

            if error_on_block_id is None: print("Blockchain is healthy")
            else:                         print(f"Block with id {error_on_block_id} is broken")

        case "Quit": raise StopIteration()

        case "See Accounts Balances":
            greeting = "Choose an account"        
            answer = OptionsMenu(accounts_ids, greeting)

            # accounts_ids is a tuple that contains username and id.
            # Must filter only id
            answer = extract_account_from_str(answer)
            
            acc_balance = db.get_account_balance(answer)
            os.system(Globals.CLEAR_COMMAND)
            print(f"Account {accounts[answer]} ({answer}) has {acc_balance} PisitiCoins")
        
        case "Send PisitiCoins":
            while True:
                greeting = "Choose your account"        
                from_id = OptionsMenu(accounts_ids, greeting)
                from_id = extract_account_from_str(from_id)

                os.system(Globals.CLEAR_COMMAND)

                greeting = "Choose the account you wish to transfer to"        
                to_id = OptionsMenu(accounts_ids, greeting)
                to_id = extract_account_from_str(to_id)

                os.system(Globals.CLEAR_COMMAND)
                
                # Getting amount            
                while True:
                    try:                    
                        amount = float(input("How many PisitiCoins to transfer? "))
                        break
                    except ValueError as e: 
                        continue
                    finally:                
                        os.system(Globals.CLEAR_COMMAND)

                if amount < 0:
                    amount *= -1

                greeting = f"You wish to transfer {amount} PisitiCoins from {from_id} to {to_id}, correct?"
                options = ["Yes", "No"]
                if OptionsMenu(options, greeting) == "Yes":
                    break
            
            # Getting random miner
            miner_id = secrets.choice(tuple(db.get_accounts_ids_and_usernames().keys()))
            block_data = {
                "from_id":  from_id,
                "to_id":    to_id,
                "amount":   amount,
                "miner_id": miner_id
            }

            try:
                create_and_chain_block(db, block_data)
                if os.environ["PRINT_STEPS"] == "True":
                    print("Transaction complete")

            except ValueError as e:         
                from_balance = block_data["from_id"]   
                print()
                print(f"Insufficient funds in account {from_id}. Aborting operation")
                print(f"Current balance: {db.get_account_balance(from_balance)} PisitiCoins")

            
            # Updating the balances of accounts involved in transaction
            for _id in (from_id, to_id, miner_id):
                db.update_user_balance(_id)

        case "Show Latest blocks":
            show_latest_blocks(db)

        case "Update All balances":
            os.system(Globals.CLEAR_COMMAND)
            print("Updating balances for all users... ", end="")
            db.update_all_balances()
            print("Done!")


    input()
    input()
    os.system(Globals.CLEAR_COMMAND)


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