import os
import random
import re
import secrets

from passlib.hash import pbkdf2_sha256

from helper import *
from OptionsMenu import *
from getpass import getpass


class Globals:
    """
    Global variables
    """

    CLEAR_COMMAND           = "cls" if os.name == "nt" else "clear"
    LOGGED_IN_AS            = None
    PBKDF2_SHA256_SALT_SIZE = 16
    PBKDF2_SHA256_ROUNDS    = 10000


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


def authenticate_user(db: BlockChain, password: str) -> None:
    """
    Authenticates a user against a sqlite3 connection given a password.
    Uses PBKDF2.
    Sets the account's id into Globals.LOGGED_IN_AS if match found.   
    """

    # TODO: Need to take in the salt from db into consideration
    for acc_id in db.get_accounts_ids_and_usernames().keys():
        if pbkdf2_sha256.verify(password, acc_id):
            Globals.LOGGED_IN_AS = acc_id
            return


def check_block_chain_health(db: BlockChain) -> None:
    """
    BlockChain.check_chain_health() call
    """

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

    error_on_block_id = db.check_chain_health(amount_blocks)

    if error_on_block_id is None: print("Blockchain is healthy")
    else:                         print(f"Block with id {error_on_block_id} is broken")


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


def log_in(db: BlockChain) -> None:
    """ Prompts for passphrase and attempts to authenticate against a db """

    while True:
        os.system(Globals.CLEAR_COMMAND)
        passphrase = getpass.getpass(prompt = "Passphrase: ")      

        # Filtering out invalid passphrases
        if passphrase == "":
            print("Invalid passphrase. Please try again\n")
            continue

        break

    authenticate_user(db, passphrase)


def log_out(*args) -> None:
    """
    Logs user out by setting Globals.LOGGED_IN_AS to None.
    Every argument is IGNORED. 
    This is done for simplicity.
    """

    Globals.LOGGED_IN_AS = None


def get_all_accounts_pretty(db: BlockChain) -> tuple:
    """
    Returns a pretty formatted tuple of strings with usernames and ids for all users
    """

    accounts = db.get_accounts_ids_and_usernames()
    max_len = max([len(username) for username in accounts.values()])
    
    return tuple(f"{username}" + " " * (max_len + 1 - len(username)) + f"({_id})" for _id, username in accounts.items())


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
        "Check Block Chain health",
        "Fix Block Chain",
        "Remine All Blocks",
        "Show Latest blocks",
        "Quit"
    )

    logged_in = (
        "See Accounts Balances",
        "Send PisitiCoins",
        "Update All balances",
        "Check Block Chain health",
        "Fix Block Chain",
        "Remine All Blocks",
        "Show Latest blocks",
        "Log Out",
        "Quit"
    )

    if Globals.LOGGED_IN_AS is None: return not_logged_in
    else:                            return logged_in


def print_accounts_balances(db: BlockChain, accounts_pretty: tuple) -> None:
    """
    Prompts for an account and pretty prints its balance
    """

    greeting = "Choose an account"        
    answer = OptionsMenu(accounts_pretty, greeting)

    # accounts_ids is a tuple that contains username and id.
    # Must filter only id
    acc_id = re.findall("\((.*)\)", answer)[0].rstrip()

    # If simply print answer, there may be too many white spaces between username
    # and account id.
    # Will filter username out and create new string to print
    username = re.findall("(^.*)\(", answer)
    try:
        username = username[0].rstrip() + " "
    except IndexError as e:
        username = ""

    corrected_username_and_id = username + acc_id
    
    acc_balance = db.get_account_balance(acc_id)
    os.system(Globals.CLEAR_COMMAND)
    print(f"Account {Colors.BOLD}{corrected_username_and_id}{Colors.ENDC} has {Colors.BOLD}P$ {acc_balance}{Colors.ENDC}")


def show_latest_blocks(db: BlockChain) -> None:
    """
    Pretty prints amount of blocks determined by user
    """

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


def sign_up(db: BlockChain) -> None:
    """
    Creates a user based on a passphrase given by the user.
    Uses passlib.hash.pbkdf2_sha256 to derive the hash to be stored in the database.
    Uses Globals.PBKDF2_SHA256_SALT_SIZE and Globals.PBKDF2_SHA256_ROUNDS variables
    """

    os.system(Globals.CLEAR_COMMAND)
    username = input("Username (Optional): ")

    while True:
        passphrase = getpass("Passphrase: ")
        if passphrase != "": break

    passphrase_hash = pbkdf2_sha256.using(salt_size = Globals.PBKDF2_SHA256_SALT_SIZE, rounds = Globals.PBKDF2_SHA256_ROUNDS).hash(passphrase)

    db.set_new_user(
    {
        "id": passphrase_hash,
        "username": username    
    }
    )


def update_all_balances(db: BlockChain) -> None:
    """
    Simple call of database for full balances update 
    """

    os.system(Globals.CLEAR_COMMAND)
    print("Updating balances for all users... ", end="")
    db.update_all_balances()
    print("Done!")


def run_interface(db_path: str) -> None:
    """ Runs the main interface"""

    greeting = get_interface_greeting()
    
    # Constants
    os.environ["PRINT_STEPS"] = "True"

    options = get_interface_options()    
    os.system(Globals.CLEAR_COMMAND)

    # Creating a connection to the database
    db = BlockChain(db_path)
    pretty_accounts = get_all_accounts_pretty(db)

    answer = OptionsMenu(options, greeting)

    match answer:
        case "Check Block Chain health": check_block_chain_health(db)

        case "Log In": log_in(db)

        case "Sign Up": sign_up(db)

        case "Log Out": log_out(db)

        case "Quit": raise StopIteration()

        case "See Accounts Balances": print_accounts_balances(db, pretty_accounts)
        
        case "Send PisitiCoins":
            while True:
                greeting = "Choose your account"        
                from_id = OptionsMenu(pretty_accounts, greeting)
                from_id = extract_account_from_str(from_id)

                os.system(Globals.CLEAR_COMMAND)

                greeting = "Choose the account you wish to transfer to"        
                to_id = OptionsMenu(pretty_accounts, greeting)
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

        case "Show Latest blocks":  show_latest_blocks(db)

        case "Update All balances": update_all_balances(db)

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