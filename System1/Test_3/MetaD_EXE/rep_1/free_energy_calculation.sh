bash reweight.sh -x sys1.xtc
python block_analysis.py

if [ -d "analysis" ]
then
    :
else
    mkdir analysis
fi 
mv COLVAR_analysis analysis
mv plumed_analysis.dat analysis
mv weights.dat analysis
mv *png analysis
