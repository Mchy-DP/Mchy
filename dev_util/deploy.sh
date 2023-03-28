#!/bin/bash

#Force workspace location
cd "$(dirname "$0")/.."

build_dir_name="b${mchy_build_number:-_prime}"

echo "> clean"
mkdir -p releases/latest
touch releases/temp.temp
rm -r releases/*
mkdir -p "releases/$build_dir_name"

echo "> build deployment exe"
pyinstaller --name mchy --onefile --distpath "./releases/$build_dir_name" --workpath "./releases/$build_dir_name/build_data" --specpath "./releases/$build_dir_name" "mchy/__main__.py"


if [ -f "releases/$build_dir_name/mchy.exe" ];
then 
    echo "> deploy executable build succeeded!";
    cp "releases/$build_dir_name/mchy.exe" ""releases/latest/mchy.exe""
else
    echo "> deploy executable build failed!";
    echo ">> Listing releases files"
    ls -l releases
    echo ">> Listing `releases/$build_dir_name` files"
    ls -l "releases/$build_dir_name"
    exit 1;
fi
