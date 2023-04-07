
#Force workspace location
cd "$(dirname "$0")/.."

echo "> clean"
mkdir -p releases/latest/dp
touch releases/latest/dp/temp.temp
rm -r releases/latest/dp/*

echo "========================="
echo ""

# TEST 1
mkdir -p releases/latest/dp/test1
echo "> run mchy: test1"
./releases/latest/mchy.exe -v -o ./releases/latest/dp/test1 --log-file ./releases/latest/dp/test1/mchy.log --overwrite-log ./.github/.mchy_aux_files/deploy_validate_prog.mchy

echo "> validating output"
if [ -f "releases/latest/dp/test1/Deploy Validate Prog/generated.txt" ];
then 
    echo "> deployment generated datapack 'test1', test succeeded";
else
    echo "> Datapack did not generate 'test1' as expected, test failed!";
    exit 1;
fi

echo ""
echo "-------------------------"
echo ""

# TEST 2: Fireball staff
mkdir -p releases/latest/dp/test2_fireball
echo "> run mchy: test2_fireball"
./releases/latest/mchy.exe -v -o ./releases/latest/dp/test2_fireball --log-file ./releases/latest/dp/test2_fireball/mchy.log --overwrite-log ./examples/fireball_staff/fireball_staff.mchy

echo "> validating output"
if [ -f "releases/latest/dp/test2_fireball/Fireball Staff/generated.txt" ];
then 
    echo "> deployment generated datapack 'test2_fireball', test succeeded";
else
    echo "> Datapack did not generate 'test2_fireball' as expected, test failed!";
    exit 1;
fi

echo ""
echo "-------------------------"
echo ""

echo "All tests passed!"
