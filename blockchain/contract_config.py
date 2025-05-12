contract_address = "0xYourDeployedContractAddress"  # Replace with Remix deployed address

contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "hash",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "name": "ProofLogged",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "hash",
                "type": "string"
            }
        ],
        "name": "logProof",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
