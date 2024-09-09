#!/bin/bash 

cd $( dirname -- "$0"; )
python ./DatasetEditor.py
read -p "Press enter to continue"