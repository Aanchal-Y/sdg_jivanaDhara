// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProofStore {
    struct Proof {
        address uploader;
        string hash;   // SHA-256 or keccak256 hash of record
        string meta;   // JSON string (avoid PII)
        uint256 timestamp;
    }

    mapping(string => Proof) public proofs;

    event ProofStored(address indexed uploader, string indexed hash, string meta, uint256 timestamp);

    function storeProof(string calldata _hash, string calldata _meta) external {
        proofs[_hash] = Proof({
            uploader: msg.sender,
            hash: _hash,
            meta: _meta,
            timestamp: block.timestamp
        });
        emit ProofStored(msg.sender, _hash, _meta, block.timestamp);
    }

    function getProof(string calldata _hash) external view returns (Proof memory) {
        return proofs[_hash];
    }
}
