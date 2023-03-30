
#Force workspace location
cd "$(dirname "$0")/.."

echo "> clean"
mkdir -p releases/latest/dp
touch releases/latest/dp/temp.temp
rm -r releases/latest/dp/*

echo "> run mchy"
./releases/latest/mchy.exe -v -o ./releases/latest/dp --log-file ./releases/latest/dp/mchy.log --overwrite-log ./.github/.mchy_aux_files/deploy_validate_prog.mchy

exit 1;  # Force failure temp
echo "> validating output"
if [ -f "releases/latest/dp/Deploy Validate Prog/generated.txt" ];
then 
    echo "> deployment generated datapack, test succeeded";
else
    echo "> Datapack did not generate as expected, test failed!";
    exit 1;
fi

