import os
import sqlite3

class database():
    def __init__(self, db_path: str, path_is_relative = True) -> None:
        # Changing the current directory in order to use a relative path to the database
        if path_is_relative:
            os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

        # Check if the database file exists
        if not os.path.exists(db_path):
            raise FileNotFoundError("Connection to the database unsuccessful")

        self.conn = sqlite3.connect(db_path)      
        self.cursor = self.conn.cursor()

        # Configure the cursor to return rows as dictionaries - For get methods
        self.cursor.row_factory = sqlite3.Row

        print("Connection OPENED")

        self.block_chain_columns = (
            "previous_hash",
            "from_id",
            "to_id",
            "amount",
            "miner_id",
            "miner_reward",
            "nonce",
            "hash"        
        )


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


    def get_all_blocks_one_by_one(self, id_order_asc = True) -> dict:
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


    def set_block(self, block: dict) -> None:
        """
        Writes a block into the database
        """

        # Checking the block keys
        if tuple(block.keys()) != self.block_chain_columns:
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


if __name__ == '__main__':
    conn = "Hwey"
    db = database("db/PisitiCoin.sqlite3")
    
    b = {
            "previous_hash": "0x000483482315e330501e9e271e3500b1b46d4ccf6f010ab064b195bfb3cb5339",
            "from_id": "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf",
            "to_id": "0x2b5ad5c4795c026514f8317c7a215e218dccd6cf",
            "amount": 1.0,
            "miner_id": "0x6d40a2899b0d4f99a45450a855d457497285c3c9",
            "miner_reward": 10000.0,
            "nonce": 391,
            "hash": "0x0059d718cf909b0ea59b6f79a53b23559b17e6ade197c748274c806da7b27569"
        }

    db.set_block(b)