from web3 import Web3
import json

# Connect to Ganache
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Set contract address (from your deployment)
contract_address = web3.to_checksum_address("0xDA0bab807633f07f013f94DD0E6A4F96F8742B53")

# Use the first Ganache account
account = web3.eth.accounts[0]

# ABI of your contract
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "hash", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "ProofLogged",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "string", "name": "hash", "type": "string"}],
        "name": "logProof",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Instantiate contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to log proof hash to blockchain
def log_to_blockchain(proof_hash):
    tx = contract.functions.logProof(proof_hash).transact({
        'from': account,
        'gas': 100000
    })
    receipt = web3.eth.wait_for_transaction_receipt(tx)
    return receipt.transactionHash.hex()

# Example usage
if __name__ == "__main__":
    hash_value = "example_hash_123"
    tx_hash = log_to_blockchain(hash_value)
    print(f"Transaction hash: {tx_hash}")
