#!/bin/bash

#Force workspace location
cd "$(dirname "$0")/.."

echo "> clean"
mkdir -p mchy/built
touch mchy/built/temp.temp
rm -r mchy/built/*

echo "> build antlr"
java -Xmx500M -cp "/usr/local/lib/antlr-4.10-complete.jar:$CLASSPATH" org.antlr.v4.Tool -Dlanguage=Python3 -no-listener -visitor -o "mchy/built" "grammar/Mchy.g4"

if [ -f "mchy/built/MchyParser.py" ] && [ -f "mchy/built/MchyVisitor.py" ];
then 
    echo "> antlr build succeeded!";
else
    echo "> antlr build failed!";
    echo ">> Listing built files"
    ls -l mchy/built
    first_file=$(ls | head -n 1)
    echo ">> Initial contents of '$first_file'"
    head -n 15 $first_file
    exit 1;
fi

