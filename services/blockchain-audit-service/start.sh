#!/bin/bash

# Navigate to the script's directory (ensures it works regardless of where it's called from)
cd "$(dirname "$0")"

echo "========================================="
echo "Starting Blockchain Audit Service"
echo "========================================="

# 1. Start setup for the local blockchain
echo "Initializing local blockchain..."
cd blockchain
npm install

# Kill any existing hardhat node on 8545 to prevent port conflicts
echo "Cleaning up any existing old nodes on 8545..."
fuser -k 8545/tcp 2>/dev/null

echo "Starting Hardhat node in background..."
npx hardhat node --hostname 0.0.0.0 > hardhat_node.log 2>&1 &
HARDHAT_PID=$!

echo "Waiting for blockchain node to boot (5 seconds)..."
sleep 5

echo "Deploying Smart Contract to local blockchain..."
npx hardhat run scripts/deploy.js --network localhost

echo "========================================="
echo "Blockchain Node is running and Smart Contract deployed."
echo "Keep this terminal open! Press CTRL+C to stop."
echo "========================================="

# Keep script alive to keep the background node running
wait $HARDHAT_PID
