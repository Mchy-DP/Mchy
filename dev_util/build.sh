#!/bin/bash

#Force workspace location
cd "$(dirname "$0")/.."

echo "> clean"
mkdir -p mchy/built
touch mchy/built/temp.temp
rm -r mchy/built/*

echo "> build antlr"
java -cp "/usr/local/lib/antlr-4.9.3-complete.jar:$CLASSPATH" org.antlr.v4.Tool -Dlanguage=Python3 -no-listener -visitor -o mchy/built grammar/Mchy.g4 && echo "> antlr built successfully!"

