#! /bin/bash
set -e   # exit upon error 

# some default values
colvar_i=COLVAR
colvar_o=COLVAR_analysis
plumed=plumed_analysis.dat
n_CVs=1
kbT=2.4777090399459767  # T=298

while getopts "ic:oc:p:x:n:" opt; do
    case $opt in
    ic) colvar_i=${OPTARG};;   # the input COLVAR file for the plumed driver
    oc) colvar_o=${OPTARG};;   # the output COLVAR file for the plumed driver
    p) plumed=${OPTARG};;      # the input plumed file for the plumed driver
    x) xtc=${OPTARG};;         # the xtc file for the plumed driver
    n) n_CVs=${OPTARG};;       # the number of collective variables 
    kt) kbT=${OPTARG};;        # the conversion factor from kbT to kJ/mol 
    esac
done

# plumed driver --plumed $plumed --noatoms
plumed driver --plumed $plumed --mf_xtc sys3.xtc
bmax=`awk 'BEGIN{max=0.}{if($1!="#!" && $4>max)max=$4}END{print max}' $colvar_o`
awk '{if($1!="#!") print $3,exp(($4-bmax)/kbt)}' kbt=$kbT bmax=$bmax $colvar_o > weights.dat







