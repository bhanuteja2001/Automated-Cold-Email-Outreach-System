#!/bin/bash

for i in {1..30}
do
    python3 sendsoon.py
    sleep 10  # Wait for 10 seconds before the next iteration
done