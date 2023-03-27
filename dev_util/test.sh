#!/bin/bash

#Force current location
cd "$(dirname "$0")/.."

echo "> testing:"
python -m pytest "tests/"