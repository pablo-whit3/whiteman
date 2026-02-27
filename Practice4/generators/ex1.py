def square_gen(n):
    for i in range(1,n+1):
        yield i**2
n=int(input())
for square in square_gen(n):
    print(square)