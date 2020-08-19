import numpy as np 

fes = [] 
for i in range(20):
    f = open(f"rep_{i + 1}/sum_hills_log.txt", 'r')
    lines = f.readlines()
    f.close()

    line_n = 0
    for l in lines:
        line_n += 1
        if "Free energy difference averaging" in l:
            fes.append(float(lines[line_n - 1].split(':')[-1]))

print(max(fes), min(fes)) 
print(np.mean(fes))
print(np.std(fes))