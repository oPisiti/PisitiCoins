# PisitiCoins

#### Video Demo: https://youtu.be/HuzzJ8RMxxg

#### Description:
An exercise to better understand the workings of blockchains and cryptocurrencies.
Completely made with python and a sqlite3 database, implements the key features of a blockchain, such as:
- Distributable: every block must exist and be in its place in order for the chain to be healthy;
- Proof of Work: done by randomly chosen miners;
- Secure: PBKDF authentication, with the use of salts;
- Fast checking of chain integrity 

Is Packaged with a custom CLI:

![Screenshot from 2023-06-27 23-37-20](https://github.com/oPisiti/PisitiCoins/assets/78967454/8bae5582-5174-47a0-a30e-f3a04f001394)


Blocks stored in the database contain the following nodes:

![Screenshot from 2023-06-27 23-38-53](https://github.com/oPisiti/PisitiCoins/assets/78967454/0c61fb58-4b35-4b82-bda8-6ff1a1d2193a)


#### Custom made:
  - SHA256 implementation
  - CLI interface
  - Options menu
  - Wrapper functions for communication with this specific database

## Features
### Log In/Out and Sign Up
An account id is derived using PBKDF2 with 10,000 rounds and 16 bytes long salts. Only such id is stored in the database.

Logging in repeats the process for every salt stored and matches its corresponding id.

Database is pre-populated accounts, whose passphrases are each one of the lower case letters from "a" to "m".

### Check Block Chain health
Rehashes every block, in order, to determine inconsistencies. 

### Delete/Edit Block
Breaks chain integrity until fixing or remining of all blocks is executed.

### Fix Block Chain
Remines necessary blocks.

### Remine All Blocks
Remines every block and tries to figure out a non destructive way of fixing the chain.

### See Accounts Balances
Prompts the user for an account, then print its balance.

### Send PisitiCoins
Requires user to be logged in and have a sufficiently large balance.

### Show Latest blocks
Pretty prints a blocks's information.

### Update All balances
Recalculates every user's balance by going through every block, in order.


## Usage
Recomended using a virtual environment.

Install dependencies
```python3
pip install -r requirements.txt
``` 

Run 
```python3
python3 src/PisitiCoin.py. 
```

Create a new account or log in to one of the existing ones whose passphrases are each one of the lower case letters from "a" to "m".

Comes with pre populated blockchain. Give it a try!
