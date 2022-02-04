#! /bin/bash
set -e 
bash reweight.sh -x sys2.xtc
python block_analysis.py

if [ -d "analysis" ]
then
    :
else
    mkdir analysis
fi 
mv COLVAR_analysis analysis
mv *png analysis
mv fes_bsize* analysis
