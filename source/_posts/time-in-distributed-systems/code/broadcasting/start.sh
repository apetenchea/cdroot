#!/bin/bash

for port in "$@"; do
    python main.py --port "$port" --ports "$@" &
done
