# find maximum value of bias
bmax=`awk 'BEGIN{max=0.}{if($1!="#!" && $3>max)max=$3}END{print max}' COLVAR`

# print phi values and weights
awk '{if($1!="#!") print $2,exp(($3-bmax)/kbt)}' kbt=2.4777090399459767 bmax=$bmax COLVAR > theta.weight
