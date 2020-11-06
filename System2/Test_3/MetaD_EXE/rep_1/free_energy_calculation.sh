bash reweight.sh -x sys2.xtc
python block_analysis.py

if [ -d "analysis" ]
then
    :
else
    mkdir analysis
fi 
mv COLVAR_analysis analysis
mv COLVAR_awk analysis
mv weights.dat analysis
mv *png analysis
mv fes_bsize_* analysis
