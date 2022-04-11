import json

from solcx import compile_standard

from web3 import Web3

# read the source code
with open("./SimpleStorage.sol", "r") as file:
    contract = file.read()

# compile contract
compiled_contract = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": contract}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.9",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_contract, file)

# get bytecode and abi
byte_code = compiled_contract["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = compiled_contract["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))

chain_id = 1337
priv_key = "0xbbfbee4961061d506ffbb11dfea64eba16355cbf1d9c29613126ba7fec0aed5d"
address = "0x66aB6D9362d4F35596279692F0251Db635165871"

contract = w3.eth.contract(abi=abi, bytecode=byte_code)

nonce = w3.eth.getTransactionCount(address)

# create, sing and send transaction
tx = contract.constructor().buildTransaction(
    {"chainId": chain_id, "from": address, "nonce": nonce}
)

tx = w3.eth.account.sign_transaction(tx, private_key=priv_key)
tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# operate on contract
contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# make call on contract
print("data() ", contract.functions.data().call())

# eth_call doesn't change the state
contract.functions.store("New text").call()
print("data() ", contract.functions.data().call())

# make transaction to change state on chain
tx = contract.functions.store("New text").buildTransaction(
    {"chainId": chain_id, "from": address, "nonce": nonce + 1}
)
tx = w3.eth.account.sign_transaction(tx, private_key=priv_key)
tx_hash = w3.eth.send_raw_transaction(tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("data() ", contract.functions.data().call())
