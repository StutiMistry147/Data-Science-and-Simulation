#!/bin/bash

# Script to run Spin model checker on the Promela model

echo "=============================================="
echo "Running Concurrency Verification with Spin"
echo "=============================================="

# Check if spin is installed
if ! command -v spin &> /dev/null; then
    echo "Spin is not installed. Installing..."
    
    # For Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y spin
    # For macOS
    elif command -v brew &> /dev/null; then
        brew install spin
    else
        echo "Please install Spin manually from: http://spinroot.com/spin/Man/README.html"
        exit 1
    fi
fi

cd "$(dirname "$0")"

echo "1. Generating verifier from Promela model..."
spin -a detection_model.pml

echo "2. Compiling verifier..."
gcc -o pan pan.c

echo "3. Running verification..."
echo "----------------------------------------------"

# Run basic verification
./pan -a

echo "----------------------------------------------"
echo "4. Running simulation (example execution)..."
echo "----------------------------------------------"

# Generate a random simulation
spin -p -s -r -u100 detection_model.pml | head -50

echo "----------------------------------------------"
echo "5. Checking for deadlocks..."
./pan -l

echo "=============================================="
echo "Verification complete!"
echo "=============================================="

# Clean up
rm -f pan pan.* pan.exe
