import numpy as np

f = open('./running_record.txt', 'r')
lines = f.readlines()
print(lines[0].split()[0] == 'divide_points')
print(np.arccos(1))
a = [0,1,2,3,4,5,6]
b = [55,66,77]
c = a + b
c.pop()
print(a,b,c)
print(np.float32(0.6516549815218541652618))


