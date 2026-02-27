import math
n=int(input())
l=int(input())
S=n*l**2/4/math.tan(math.pi/n)
print(round(S))