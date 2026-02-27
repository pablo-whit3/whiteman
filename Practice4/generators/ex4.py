def square_gen(a, b):
    for i in range(a,b+1):
        yield i**2
a, b = map(int, input().split())
for square in square_gen(a, b):
    print(square)