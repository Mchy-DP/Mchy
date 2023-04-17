#!/bin/bash

#Force current location
cd "$(dirname "$0")/.."

echo "> testing:"
python -m pytest --cov-report html --cov-config=./dev_util/.res/normal.coveragerc --cov=mchy "tests/"