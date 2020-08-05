import numpy as np

fes = []
for i in range(17):
    f = open(f'rep_{i + 1}/EXE_histogram_results.txt', 'r')
    lines = f.readlines()
    f.close()

    line_n = 0
    for l in lines:
        line_n += 1
        if 'The average weights' in l:
            fes.append(float(lines[line_n].split()[-1]))
print(fes)
print(np.mean(fes))
print(np.std(fes))

