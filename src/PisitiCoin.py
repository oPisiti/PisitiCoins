import os
import random
import re
import secrets

from getpass import getpass
from helper import *
from OptionsMenu import *
from passlib.hash import pbkdf2_sha256
from pynput.keyboard import Controller


class Globals:
    """
    Global variables
    """

    CLEAR_COMMAND           = "cls" if os.name == "nt" else "clear"
    LOGGED_IN_ACCOUNT_ID    = None
    LOGGED_IN_USERNAME      = None
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


class SpecialChars:
    CHECK_MARK = f"{Colors.OKGREEN}\u2714{Colors.ENDC}"
    FAIL_MARK  = f"{Colors.FAIL}\u2718{Colors.ENDC}"


def authenticate_user(db: BlockChain, password: str) -> None:
    """
    Authenticates a user against a sqlite3 connection given a password.
    Uses PBKDF2.
    Sets the account's id into Globals.LOGGED_IN_AS if match found.   
    """

    ids_and_usernames = db.get_accounts_ids_and_usernames()

    for acc_id in ids_and_usernames.keys():
        if pbkdf2_sha256.verify(password, acc_id):
            Globals.LOGGED_IN_ACCOUNT_ID = acc_id
            Globals.LOGGED_IN_USERNAME   = ids_and_usernames[acc_id]
            return


def check_block_chain_health(db: BlockChain) -> None:
    """
    BlockChain.check_chain_health() call
    """

    os.system(Globals.CLEAR_COMMAND)

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
    else:                         print(f"Block {Colors.FAIL}#{error_on_block_id}{Colors.ENDC} is broken")


def choose_a_block_from_chain(db: BlockChain, message: str) -> str:
    """
    Queries the database for available blocks.
    Prompts the user for a block.
    Blocks are prepended with an indication of where the chain is healthy or not.
    Returns the id of the chosen block, as an int
    """

    blocks_ids = list(db.get_blocks_ids())
    error_on_block_id = db.check_chain_health(-1)
    block_state = "\u2714"

    # Adding check mark or cross to the start of the ids
    for i in range(len(blocks_ids)):
        if blocks_ids[i] == error_on_block_id: block_state = "\u2718"

        blocks_ids[i] = block_state + " " + str(blocks_ids[i])


    return int(options_menu(blocks_ids, message)[2:])


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


def delete_block(db: BlockChain) -> None:
    """
    Prompts for a block and deletes it from the database
    """

    message = "Which block do you wish to delete?"
    
    answer = choose_a_block_from_chain(db, message)

    message = f"Are you sure you wish to delete block {Colors.BOLD}{Colors.WARNING}#{answer}{Colors.ENDC}?"
    is_sure = options_menu(("Yes", "No"), message)

    if is_sure == "Yes": 
        db.delete_block(answer)
        os.system(Globals.CLEAR_COMMAND)
        input(f"Block {Colors.BOLD}#{answer}{Colors.ENDC} deleted")


def edit_block(db: BlockChain) -> None:
    """
    Allows the user to edit every item of a block.
    Prompt the user, given all the available blocks.
    """

    message = "Choose a block:"

    chosen_block_id = choose_a_block_from_chain(db, message)

    # Prompting for a column
    block = db.get_block_by_id(chosen_block_id)
    block_lines = get_pretty_block(block)

    edit_line = options_menu(block_lines[1:], block_lines[0])
    chosen_option_index = block_lines.index(edit_line)

    # Adding listener for keyboard in order to prefill it and make a line editable
    keyboard = Controller()

    os.system(Globals.CLEAR_COMMAND)

    # Printing the lines and making space for the one that should be editable
    for line in block_lines:
        if line != edit_line: print(line)
        else:                 print()

    # Making an editable line
    editable = re.findall(":\s*(.*)", edit_line)[0]
    fixed = edit_line[0:edit_line.index(editable)]

    print(Colors.UPONELINE * (len(block_lines) - chosen_option_index), end="")
    print(fixed, end="")
    keyboard.type(editable)
    edited = input()

    # --- MATCHING to decide the equivalent column name on the databases ---    
    column_match = {
    "previous hash":     "previous_hash",
    "from":              "from_id",
    "to":                "to_id",
    "amount (p$)":       "amount",
    "mined by":          "miner_id",
    "miner reward (p$)": "miner_reward",
    "nonce":             "nonce",
    "hash":              "hash"   
    }

    column_name = column_match[re.findall("(^.*):", fixed)[0].lower()]

    # TODO: Editing number, i.e. amount, writes wrong number to db or straight up shit
    db.update_any_column_any_block(chosen_block_id, column_name, edited)

    pass


def extract_id_from_string(string: str) -> str:
    """
    Extracts passlib.hash.pbkdf2_sha256 hash from a string, if between parenthesis.
    Example: "Luna   ($pbkdf2-sha256$10000$WGtNiTHmHGMsZUzJGYMQIg$bjHZlH6YI8wwfVaThD3LNrn5nd6VgLnG.xfFie1qRus)"
    Returns "$pbkdf2-sha256$10000$WGtNiTHmHGMsZUzJGYMQIg$bjHZlH6YI8wwfVaThD3LNrn5nd6VgLnG.xfFie1qRus"
    """

    return re.findall("\((.*)\)", string)[0].rstrip()


def fix_block_chain(db: BlockChain) -> None:
    """
    Detects a chain inconsistency and fixes it
    """

    error_on_block_id = db.check_chain_health(-1)

    if error_on_block_id is None: 
        os.system(Globals.CLEAR_COMMAND)
        print("Block Chain is healthy")
        return 

    blocks_ids = db.get_blocks_ids()
    error_block_index = blocks_ids.index(error_on_block_id)

    os.system(Globals.CLEAR_COMMAND)
    print(f"Fixing blocks...")
    for i in range(error_block_index, len(blocks_ids)):

        # Updating previous_hash field 
        db.update_previous_hash_by_id(blocks_ids[i], blocks_ids)

        db.remine_block(blocks_ids[i])

        print(f"{SpecialChars.CHECK_MARK} #{blocks_ids[i]}")
        
    print("Done!")


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
    (f"{Colors.OKCYAN}Logged in as {Colors.BOLD}{Globals.LOGGED_IN_USERNAME} {Globals.LOGGED_IN_ACCOUNT_ID}{Colors.ENDC}\n" if Globals.LOGGED_IN_ACCOUNT_ID is not None else \
     f"{Colors.FAIL}Not logged in{Colors.ENDC}\n")


def get_interface_options() -> tuple:
    """
    Returns updated options
    """

    not_logged_in = (
        "Log In",
        "Sign Up",
        "Check Block Chain health",
        "Fix Block Chain",
        "Remine All Blocks",
        "See Accounts Balances",
        "Show Latest blocks",
        "Update All balances",
        "Edit a Block",
        "Delete Block",
        "Quit"
    )

    logged_in = (
        "Log Out",
        "Check Block Chain health",
        "Fix Block Chain",
        "Remine All Blocks",
        "See Accounts Balances",
        "Send PisitiCoins",
        "Show Latest blocks",
        "Update All balances",
        "Edit a Block",
        "Delete Block",
        "Quit"
    )

    if Globals.LOGGED_IN_ACCOUNT_ID is None: return not_logged_in
    else:                                    return logged_in


def get_pretty_block(block: dict) -> tuple:
    """
    Returns a tuple of string containing a pretty print of every line on a block
    
    Raises KeyError if 'block' does not contain the following keys:
        - "id"
        - "previous_hash"
        - "from_id"
        - "to_id"
        - "amount"
        - "miner_id"
        - "miner_reward"
        - "nonce"
        - "hash"   
    """

    required_keys = (
        "id",
        "previous_hash",
        "from_id",
        "to_id",
        "amount",
        "miner_id",
        "miner_reward",
        "nonce",
        "hash"   
    )

    if required_keys != tuple(block.keys()):
        raise KeyError(f"Mismatched keys. Required keys: {required_keys}")

    # CAREFUL when changing this. May create serious bugs.
    # Check the matching made inside edit_block() to determine if that breaks.
    # Such matching is used to figure out the corresponding column name on the database
    return (
        f"Block {Colors.BOLD}#{block['id']}{Colors.ENDC}",
        f"Previous Hash:     {block['previous_hash']}",
        f"From:              {block['from_id']}",
        f"To:                {block['to_id']}",
        f"Amount (P$):       {block['amount']}",
        f"Mined By:          {block['miner_id']}",
        f"Miner Reward (P$): {block['miner_reward']}",
        f"Nonce:             {block['nonce']}",
        f"Hash:              {block['hash']}"
    )


def log_in(db: BlockChain) -> None:
    """ Prompts for passphrase and attempts to authenticate against a db """

    while True:
        os.system(Globals.CLEAR_COMMAND)
        passphrase = getpass(prompt = "Passphrase: ")      

        # Filtering out invalid passphrases
        if passphrase == "":
            print("Invalid passphrase. Please try again\n")
            input()
            continue

        break

    authenticate_user(db, passphrase)


def log_out() -> None:
    """
    Logs user out by setting Globals.LOGGED_IN_AS to None.
    """

    Globals.LOGGED_IN_ACCOUNT_ID = None
    Globals.LOGGED_IN_USERNAME   = None


def print_accounts_balances(db: BlockChain, accounts_pretty: tuple) -> None:
    """
    Prompts for an account and pretty prints its balance
    """

    greeting = "Choose an account"        
    answer = options_menu(accounts_pretty, greeting)

    # accounts_ids is a tuple that contains username and id.
    # Must filter only id
    acc_id = extract_id_from_string(answer)

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


def remine_all_blocks(db: BlockChain) -> None:
    """
    Remines all blocks, independently of their health state
    """

    blocks_ids = db.get_blocks_ids()

    os.system(Globals.CLEAR_COMMAND)
    print(f"Remining blocks...")
    for _id in blocks_ids:
        # Updating previous_hash field 
        db.update_previous_hash_by_id(_id, blocks_ids)

        db.remine_block(_id)

        print(SpecialChars.CHECK_MARK + f" #{_id}")

    print("Done!")


def send_pisiticoins(db: BlockChain, accounts_pretty: tuple) -> None:
    """
    Prompts user for information, creates a block and chains it.
    Uses:
        - Globals.LOGGED_IN_ACCOUNT_ID
    """

    while True:
        os.system(Globals.CLEAR_COMMAND)

        from_id = Globals.LOGGED_IN_ACCOUNT_ID

        greeting = "Choose the account you wish to transfer to"        
        to_id = options_menu(accounts_pretty, greeting)
        to_id = extract_id_from_string(to_id)

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
        if options_menu(options, greeting) == "Yes":
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


def show_latest_blocks(db: BlockChain) -> None:
    """
    Pretty prints amount of blocks determined by user
    """

    while True:
        os.system(Globals.CLEAR_COMMAND)
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
    for block in db.get_all_blocks():
        for line in get_pretty_block(block): print(line)

        if count >= amount_blocks: break
        count += 1
        print()


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
    accounts_pretty = get_all_accounts_pretty(db)

    answer = options_menu(options, greeting)

    match answer:
        case "Check Block Chain health": check_block_chain_health(db)
        case "Delete Block":             delete_block(db)
        case "Edit a Block":             edit_block(db)
        case "Fix Block Chain":          fix_block_chain(db)    
        case "Log In":                   log_in(db)
        case "Log Out":                  log_out()
        case "Quit":                     raise StopIteration()
        case "Remine All Blocks":        remine_all_blocks(db)
        case "See Accounts Balances":    print_accounts_balances(db, accounts_pretty)    
        case "Send PisitiCoins":         send_pisiticoins(db, accounts_pretty)
        case "Show Latest blocks":       show_latest_blocks(db)
        case "Sign Up":                  sign_up(db)
        case "Update All balances":      update_all_balances(db)

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