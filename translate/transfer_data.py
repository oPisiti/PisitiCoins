# Author:  Lauro França @oPisiti
# Created: 2023

import json
import sqlite3

def transfer_json_to_sqlite3(path_json: str, path_sqlite3: str) -> None:
    """ Transfers all the data from a json file into a sqlite3 database """
    # Opening the json file
    with open(path_json, "r") as f:
        json_file = json.load(f)

    bc = json_file["BlockChain"]
    pk = json_file["Public keys"]

    # Initializing the database
    conn = sqlite3.connect(path_sqlite3)
    cursor = conn.cursor()

    # Transferring data
    for block in bc:
        cursor.execute(
        """ 
        INSERT INTO block_chain (previous_hash, from_id, to_id, amount, miner_id, miner_reward, nonce, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ;""",
       (block["previous hash"],
        block["from"],
        block["to"],
        float(block["value"]),
        block["miner"],
        float(block["miner reward"]),
        block["nonce"],
        block["hash"])
        )

    for key in pk:
        cursor.execute(
        """ 
        INSERT INTO accounts (id, balance)
        VALUES (?, ?)
        ;""",
       (key,
        10_000)
       )


    # Close the cursor and the connection
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':

    transfer_json_to_sqlite3(
        path_json = "db/PisitiCoin.json",
        path_sqlite3 = "db/PisitiCoin.sqlite3",
    )
