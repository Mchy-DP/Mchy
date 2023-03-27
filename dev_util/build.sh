#!/bin/bash

#Force workspace location
cd "$(dirname "$0")/.."

echo "> clean"
touch mchy/built/temp.temp
rm -r mchy/built/*

echo "> build antlr"
cmd "/c antlr4 -Dlanguage=Python3 -no-listener -visitor -o mchy/built grammar/Mchy.g4 "

echo "> antlr built successfully!"

