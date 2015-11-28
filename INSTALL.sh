#!/bin/bash

python -c "import setuptools"

if [ $? == 0 ];then
echo "The 'setuptools' module exists."
elif [ $? == 1 ];then
wget https://bootstrap.pypa.io/ez_setup.py -O - | python - --user
fi

python setup.py install --user

echo 
echo "Please add" $PWD"/bin to the PATH."
echo 

rm -r build/ dist/ lib/pat3dem.egg-info/

