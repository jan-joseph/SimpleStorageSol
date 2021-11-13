from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

print("Installing...")
install_solc("0.6.0")

# Compile the Solidity File

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# Get Bytecode Object
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# Get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


# for Connecting to Ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the transaction count
nonce = w3.eth.getTransactionCount(my_address)

# Building the Transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

# Signing the Transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send the transaction
print("Deploying contract")
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Block Confirmation
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Deployed")


# Working with the Contract
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())

# Running a Transact Function
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
print("Updating Contract")
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
store_txn_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
txn_receipt = w3.eth.wait_for_transaction_receipt(store_txn_hash)
print("Updated!")
print(simple_storage.functions.retrieve().call())

