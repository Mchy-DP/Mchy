#!/bin/bash

#Force workspace location
cd "$(dirname "$0")/.."

build_dir_name="b${mchy_build_number:-_prime}"

echo "> clean"
mkdir -p releases
touch releases/temp.temp
rm -r releases/*
mkdir -p "releases/$build_dir_name"

echo "> build deployment exe"
pyinstaller --name mchy --onefile --distpath "./releases/$build_dir_name" --workpath "./releases/$build_dir_name/build_data" --specpath "./releases/$build_dir_name" "mchy/__main__.py"
