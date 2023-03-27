#!/bin/bash

#Force current location
cd "$(dirname "$0")/.."

echo "> Running tests (from: $(pwd))"
python -m pytest "tests/"