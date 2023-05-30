import os
import sqlite3

from SHA256 import *

class Database():
    def __init__(self, db_path: str, path_is_relative = True) -> None:
        # Changing the current directory in order to use a relative path to the database
        if path_is_relative:
            os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

        # Check if the databprevious hashase file exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"File {db_path} does not exist")

        # Trying to connect to database
        self.conn = sqlite3.connect(db_path)      

        # Testing connection
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("SELECT id FROM accounts")
        except sqlite3.Error as e:
            raise FileExistsError("Connection to the database unsuccessful")

        # Configure the cursor to return rows as dictionaries - For get methods
        self.cursor.row_factory = sqlite3.Row

        print("Connection OPENED")

        self.block_chain_columns = {
            "previous_hash",
            "from_id",
            "to_id",
            "amount",
            "miner_id",
            "miner_reward",
            "nonce",
            "hash"        
        }

    def __del__(self) -> None:
        # Close the cursor and the database connection
        self.cursor.close()
        self.conn.close()

        print("Connection CLOSED")


    def get_block_by_id(self, block_id: int) -> dict:
        """ Returns a dictionary containing all the data of a block """

        self.cursor.execute(
        """
        SELECT * 
          FROM block_chain bc 
         WHERE id = ?
        """,
        (block_id,))

        return dict(self.cursor.fetchone())


    def get_all_blocks(self, id_order_asc = True) -> dict:
        """ 
        Returns an iterator over all the blocks in the database.
        Queries one block at a time and in order of id.
        """

        self.cursor.execute(
        """
        SELECT id 
          FROM block_chain bc 
        """)

        blocks_id_list = [a[0] for a in self.cursor.fetchall()]

        # Reversing the ids order
        if not id_order_asc: blocks_id_list = blocks_id_list[::-1]

        # Queries one block at a time. Less RAM usage
        for i in blocks_id_list:
            self.cursor.execute(
            """
            SELECT * 
              FROM block_chain bc 
             WHERE id = ?
            """,
            (i,))

            yield dict(self.cursor.fetchone())


    def get_accounts_ids_and_usernames(self) -> dict:
        """ Returns a dict {id:username} containing every account id and username in the "accounts" table """

        self.cursor.execute(
        """
        SELECT id, username 
          FROM accounts
        """)

        return dict(self.cursor.fetchall())


    def get_accounts(self) -> dict:
        """ Returns a dict containing every account in the "accounts" table """

        self.cursor.execute(
        """
        SELECT * 
          FROM accounts
        """)

        return dict(self.cursor.fetchall())

    
    def get_account_balance(self, account_id: str) -> float:
        """ 
        Returns the balance of one specific account
        Raises LookupError if no account with such id exists in database
        """

        self.cursor.execute(
        """
        SELECT balance 
          FROM accounts
         WHERE id = ?
        """,
        (account_id,)
        )

        try:
            balance = dict(self.cursor.fetchone())
        except TypeError as e:
            raise LookupError(f"No account with id '{account_id}' exists")
        
        return balance["balance"]


    def update_user_balance(self, account_id: str) -> None:
        """ Updates a user's balance by looping over every transaction """

        # Getting relevant transactions/blocks
        self.cursor.execute(
            """
            SELECT from_id, to_id, amount, miner_id, miner_reward
              FROM block_chain bc 
             WHERE from_id = ?
                OR to_id = ?
                OR miner_id = ?
            """,
            (account_id, account_id, account_id)
            )

        transactions = [dict(item) for item in self.cursor.fetchall()]
        
        # Summing the transactions
        account_balance = 0
        for t in transactions:
            if   account_id == t["from_id"]:  account_balance -= t["amount"]
            elif account_id == t["to_id"]:    account_balance += t["amount"]
            elif account_id == t["miner_id"]: account_balance += t["miner_reward"]

        self.set_user_balance(account_id, account_balance)


    def update_all_balances(self) -> None:
        """ Update every user's balances """

        user_ids = tuple(self.get_accounts_ids_and_usernames().keys())
        user_balances = {id: 0 for id in user_ids}

        # Summing up every user's transactions
        for block in self.get_all_blocks():
            user_balances[block["from_id"]]  -= block["amount"]
            user_balances[block["to_id"]]    += block["amount"]
            user_balances[block["miner_id"]] += block["miner_reward"]

        # Writing to database
        for account_id, balance in user_balances.items():
            self.set_user_balance(account_id, balance)


    def set_user_balance(self, account_id: str, balance: float) -> None:    

        self.cursor.execute(
        """
        UPDATE accounts
           SET balance = ?
         WHERE id = ?
        """,
        (balance, account_id)
        )

        self.conn.commit()


    def set_block(self, block: dict) -> None:
        """
        Writes a block into the database.
        """

        # Checking the block keys
        if set(block.keys()) != self.block_chain_columns:
            raise KeyError(f"Provided block does not contain the correct keys. They are the following: {self.block_chain_columns}")

        # INSERTING THE VARIABLES DIRECTLY INTO THE STRING IS ONLY OK BECAUSE THIS DOES NOT CONTAIN USER INPUT
        # This will not be susceptible to sql injection attacks.
        # It is done here because "Parameter markers can be used only for values", as explained in https://stackoverflow.com/questions/13880786/python-sqlite3-string-variable-in-execute
        self.cursor.execute(
        """
        INSERT INTO block_chain """ + str(tuple(block.keys())) + """
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        list(block.values())
        )

        self.conn.commit()


    def assert_sqlite3_open(func):
        """ 
        Makes sure a variable exists.
        Raises AssertionError otherwise
        """

        def wrapper(*args, **kwargs):
            if (conn_var_name not in locals()) and (conn_var_name not in globals()):
                raise AssertionError(f"No variable called '{conn_var_name}' exists")

            if not isinstance(conn_var_name, sqlite3.Connection):
                raise AssertionError(f"The variable {conn_var_name} does not correspond to a sqlite3 database file")

            value = func(*args, **kwargs)

            return value

        return wrapper


class Block():
    # TODO: The block id should be determined by the database itself
    # Also, the previous hash should be determined by a query
    def __init__(self, db: Database, block_info: dict) -> None:
        """
        Creates a Block object
        Database connection parameter necessary in order to determine the previous block's hash
        """

        # Variables
        self.block_has_been_mined = False

        # Constants
        self.difficulty    = 2
        self.miner_reward  = 10000
        self.clear_command = "cls" if os.name == "nt" else "clear"

        required_keys = (
            "from_id",
            "to_id",
            "amount",
            "miner_id"
        )
        
        if tuple(block_info.keys()) != required_keys:
            raise KeyError(
                f"""
                Keys from provided dictionary are incorrect
                Required keys: {required_keys}
                """
                )


        # Setting up the block
        self.block = block_info.copy() 
        self.block["miner_reward"] = self.miner_reward

        for b in db.get_all_blocks(id_order_asc = False):
            self.block["previous_hash"]     = b["hash"]
            break


    def mine_block(self, print_steps = False) -> None:        
        """ 
        Returns the hash of a block.
        This method determines the order of bytes in hash input.
        """

        # Full message
        base_message = self.det_partial_string_to_hash()
        nonce = 0
        compare = "0" * self.difficulty

        os.system(self.clear_command)

        # Mining block
        while True:
            if print_steps: print(f"Trying nonce {nonce}", end = "\r")

            message = base_message + hex(nonce)
            this_hash = SHA256(message)
            
            if this_hash[0 : self.difficulty] != compare:                
                nonce += 1
            else:
                os.system(self.clear_command)
                if print_steps: 
                    print(f"Block MINED. Adding {self.block['miner_reward']} to {self.block['miner_id']} as miner reward")
                    print(f"Nonce: {nonce}")
                    print(f"Hash: {this_hash}")
                    print("")
                break

        # Writing info into block
        self.block["hash"]         = "0x" + this_hash
        self.block["nonce"]        = nonce

        self.block_has_been_mined = True


    def chain_block(self, db: Database) -> None:
        """ 
        Adds a block to the chain
        Raises KeyError if block has not been mined yet
        """

        # The block needs to have been mined
        if not self.block_has_been_mined:
            raise KeyError("Block has not been mined")

        db.set_block(self.block)
      
                
    def det_partial_string_to_hash(self) -> str:
        """
        Returns a partial string containing the block's data
        """

        return  self.block["previous_hash"][2:] + \
                self.block["from_id"][2:] + \
                self.block["to_id"][2:] + \
                format(self.block["amount"], '#066x')[2:] + \
                self.block["miner_id"][2:] + \
                format(self.block["miner_reward"], '#066x')[2:] 


if __name__ == '__main__':
    pass